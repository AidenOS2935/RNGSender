from flask import Flask, jsonify, request
from discord import Webhook, Embed  # Import Embed
import aiohttp, os, dotenv, asyncio, logging, time

app = Flask(__name__)
dotenv.load_dotenv()
globalwebhook = os.getenv("GLOBAL_WEBHOOK_URL")
tenmilwebhook = os.getenv("TENMIL_WEBHOOK_URL")
embedsendtimeout = int(os.getenv("EMBED_SEND_TIMEOUT", 300))
lastglobal = int(time.time())

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embeds = []
tenmils = []

@app.route("/add", methods=["POST"])
async def add():
    # Global variables
    global embeds
    global tenmils
    global lastglobal

    # Getting the data of request
    data = request.json

    # Process for global
    if data.get("global", False):
        logger.info(f"Request received for Global. ({len(embeds)+1}/10)")
        # add embeds
        description = f"**{data['nickname']} (@{data['username']})** HAS FOUND **{data['aura']}**, **{data['chance']}**"
        if data.get("biome") and data.get("biome") != "" and data.get("biome") != "None":
            description += f" **{data['biome']}**"
        if data.get("firstfound", False):
            description += " **[FIRST FOUND!]**"
        embed = Embed(
            title="Global",
            description=description,
            color=0xff8479  # Discord color for #ff8479
        )
        embed.add_field(name="Rolls", value=str(data['rolls']), inline=True)
        embed.add_field(name="Time Discovered", value=f"<t:{data['timestamp']}:f>", inline=True)
        embed.add_field(name="Roll Luck", value=str(data['rollLuck']), inline=True)
        embeds.append(embed)

        if len(embeds) == 10:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(globalwebhook, session=session)
                    msg = await webhook.send(content="", embeds=embeds, wait=True)
                    embeds = []
                    lastglobal = int(time.time())
                    logger.info("Success: Embeds sent successfully.")
                    return jsonify({"message": "Sent"}), 201
            except Exception as e:
                logger.error(f"Error: {e}")
                return jsonify({"message": "Failed to send embeds", "error": str(e)}), 500
        elif len(embeds) >= 10:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(globalwebhook, session=session)
                    await webhook.send(content=None, embeds=embeds[:10])
                    embeds = embeds[10:]
                    lastglobal = int(time.time())
                    logger.info("Success: Embeds sent successfully (overflowing).")
                    return jsonify({"message": "Sent (overflowing)"}), 201
            except Exception as e:
                logger.error(f"Error: {e}")
                return jsonify({"message": "Failed to send embeds (overflowing)", "error": str(e)}), 500
        else:
            return jsonify({"message": "Added"}), 201
    

    # Process for 10 mils
    else:
        logger.info(f"Request received for 10 mils. ({len(tenmils)+1}/10)")
        # add 10 mils
        description = f"**{data['nickname']} (@{data['username']})** HAS FOUND **{data['aura']}**, **{data['chance']}**"
        if data.get("biome") and data.get("biome") != "" and data.get("biome") != "None":
            description += f" **{data['biome']}**"
        if data.get("firstfound", False):
            description += " **[FIRST FOUND!]**"
        embed = Embed(
            title="Rare Aura",
            description=description,
            color=0x8ea7ff  # Discord color for #8ea7ff
        )
        embed.add_field(name="Rolls", value=str(data['rolls']), inline=True)
        embed.add_field(name="Time Discovered", value=f"<t:{data['timestamp']}:f>", inline=True)
        embed.add_field(name="Roll Luck", value=str(data['rollLuck']), inline=True)
        tenmils.append(embed)

        if len(tenmils) == 10:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(tenmilwebhook, session=session)
                    await webhook.send(content=None, embeds=tenmils)
                    tenmils = []
                    logger.info("Success: 10 mils sent successfully.")
                    return jsonify({"message": "Sent"}), 201
            except Exception as e:
                logger.error(f"Error: {e}")
                return jsonify({"message": "Failed to send 10 mils", "error": str(e)}), 500
        if len(tenmils) >= 10:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(tenmilwebhook, session=session)
                    await webhook.send(content=None, embeds=tenmils[:10])
                    tenmils = tenmils[10:]
                    logger.info("Success: 10 mils sent successfully (overflowing).")
                    return jsonify({"message": "Sent (overflowing)"}), 201
            except Exception as e:
                logger.error(f"Error: {e}")
                return jsonify({"message": "Failed to send 10 mils (overflowing)", "error": str(e)}), 500        
        if len(embeds) >= 1 and int(time.time()) - lastglobal >= embedsendtimeout:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(globalwebhook, session=session)
                    await webhook.send(content=None, embeds=embeds)
                    embeds = []
                    lastglobal = int(time.time())
                    logger.info("Success: Embeds sent successfully. (timeout)")
                    return jsonify({"message": "Sent (timeout)"}), 201
            except Exception as e:
                logger.error(f"Error: {e}")
                return jsonify({"message": "Failed to send embeds", "error": str(e)}), 500
        else:
            return jsonify({"message": "Added"}), 201

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 3645))
    asyncio.run(app.run(debug=True, host="0.0.0.0", port=port))
