import logging
import datetime

import discord
from discord.ext import commands

def check_embed_is_admin_only(embed, ckey, admin_only_text):
    text_to_check = []

    if embed.title:
        text_to_check.append(embed.title)
    if embed.description:
        text_to_check.append(embed.description)

    for field in embed.fields:
        if field.name:
            text_to_check.append(field.name)
        if field.value:
            text_to_check.append(field.value)

    if not text_to_check:
        return False

    for text in text_to_check:
        lines = text.splitlines()
        for line in lines:
            lower_line = line.lower()
            if ckey.lower() not in lower_line or admin_only_text.lower() not in lower_line:
                return False

    return True


def check_embed(embed, ckey):
    if embed.title and ckey in embed.title.lower():
        return True
    if embed.description and ckey in embed.description.lower():
        return True
    for field in embed.fields:
        if field.name and ckey in field.name.lower():
            return True
        if field.value and ckey in field.value.lower():
            return True
    return False


class AdminStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.slash_command(name="ahelp_stats", description="Количество отвеченных ахелпов")
    async def ahelp_stats(self, ctx: discord.ApplicationContext, channel: discord.Option(discord.TextChannel, "Канал с ахелпами", required=True), ckey: discord.Option(str, requied=True, description="Сикей администратора")):

        ADMIN_ONLY_TEXT = "(Admin Only)"

        now = datetime.datetime.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        all_ahelps_with_mention = 0
        ahelps_without_admin_only = 0
        ahelps_with_admin_only = 0
        messages_with_mention = []

        async for message in channel.history(limit=None, after=first_day_of_month):
            for embed in message.embeds:
                if check_embed(embed, ckey):
                    if not check_embed_is_admin_only(embed, ckey, ADMIN_ONLY_TEXT):
                        all_ahelps_with_mention += 1
                        messages_with_mention.append(message)
                        break

        self.logger.info(f"Найдено {all_ahelps_with_mention} сообщений, которые не содержат Admin Only embed с упоминанием '{ckey}' в этом месяце:")

        for message in messages_with_mention:
            self.logger.info(f"- {message.author.name}: {message.content} (ID: {message.id}, Time: {message.created_at})")

        now = datetime.datetime.now()
        date = now.strftime("%m.%Y")

        answer = discord.Embed(title=f"{ctx.author.name} | {channel.name} | {date}", colour=0x41f096)

        answer.add_field(name="Общее количество", inline=False,
            value=f"Было найдено {all_ahelps_with_mention} ахелпов"
        )
        answer.add_field(name="Без Admin Only", inline=False,
            value=f"Было найдено {ahelps_with_admin_only} ахелпов"
        )
        answer.add_field(name="Admin Only", inline=False,
            value=f"Было найдено {ahelps_without_admin_only} ахелпов"
        )

        await ctx.respond(embed=answer, ephemeral=True)