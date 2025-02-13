import steam


class MyClient(steam.Client):
    async def on_ready(self) -> None:
        print(f"We have logged in as {self.user}")

    async def on_message(self, message: steam.Message) -> None:
        if message.author == self.user:
            return

        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")


client = MyClient()
client.run("username", "password")