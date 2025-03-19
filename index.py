from flask import Flask, jsonify, request
from discord import Webhook, Embed  # Import Embed
import aiohttp, os, dotenv
import asyncio  # Import asyncio

app = Flask(__name__)
dotenv.load_dotenv()
url = os.getenv("WEBHOOK_URL")

embeds = []

@app.route("/add", methods=["POST"])
async def add():
    print("Request received.")
    global embeds
    data = request.json
    # add embeds
    description = f"**{data['nickname']} (@{data['username']})** HAS FOUND **{data['aura']}**, **{data['chance']}**"
    if data.get("biome") and data.get("biome") != "" and data.get("biome") != "None":
        description += f" **[From {data['biome']}]**"
    if data.get("firstfound", False):
        description += " **[FIRST FOUND!]**"
    embed = Embed(
        title="Global",
        description=description,
        color=None
    )
    embed.add_field(name="Rolls", value=str(data['rolls']), inline=True)
    embed.add_field(name="Time Discovered", value=f"<t:{data['timestamp']}:f>", inline=True)
    embeds.append(embed)

    if len(embeds) == 10:
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, session=session)
                await webhook.send(content=None, embeds=embeds)
                embeds = []
                print("Success: Embeds sent successfully.")
                return jsonify({"message": "Sent"}), 201
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "Failed to send embeds", "error": str(e)}), 500
    if len(embeds) >= 10:
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, session=session)
                await webhook.send(content=None, embeds=embeds[:10])
                embeds = embeds[10:]
                print("Success: Embeds sent successfully (overflowing).")
                return jsonify({"message": "Sent (overflowing)"}), 201
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "Failed to send embeds (overflowing)", "error": str(e)}), 500
    else:
        return jsonify({"message": "Added"}), 201

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 3645))
    asyncio.run(app.run(debug=True, host="0.0.0.0", port=port))
