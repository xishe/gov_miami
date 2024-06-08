import disnake
from disnake.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = 1119326879564972148  # Замените на реальный ID канала
        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            embed = disnake.Embed(
                title="Добро пожаловать во фракцию Goverment",
                description="Перед началом работы, тебе нужно изменить никнейм на сервере по этой форме:\n\n"
                            "Отдел | Имя Фамилия | Static ID (для USSS)\n"
                            "Должность | Имя Фамилия | Static ID (для всех остальных)\n\n"
                            "Пример:\n"
                            "ECTF | Rick Immortal | 43642\n"
                            "Адвокат | Rick Immortal | 43642",
                color=0x2F3136,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url='https://i1.imageban.ru/out/2024/04/29/29a3ec96ab4bea5d22fb3718b991454a.png')
            embed.set_footer(text=f"ID пользователя: {member.id}")
            await channel.send(f'{member.mention}', embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))
