import discord
from discord.ext import commands
from discord import ForumChannel, app_commands
import math
import re
from collections import Counter
import random
import os

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
isOnline = {"value": False}


@bot.tree.command(name="create_thread", description="在論壇中建立串文")
@app_commands.describe(channel="論壇", name="標題", content="內容")
async def create_thread(interaction: discord.Interaction,
                        channel: ForumChannel, name: str, content: str):
  await interaction.response.defer(ephemeral=True)

  await channel.create_thread(name=name, content=content)

  await interaction.followup.send(f"主題「{name}」已建立於論壇 {channel.mention}！",
                                  ephemeral=True)


@bot.tree.command(name="search_thread", description="尋找任意論壇裡的串文")
@app_commands.describe(channel="論壇", keyword="關鍵字")
async def search_thread(interaction: discord.Interaction,
                        channel: ForumChannel, keyword: str):
  await interaction.response.defer(ephemeral=True)

  threads = channel.threads
  matching = []
  for thread in threads:
    if thread.parent_id != channel.id:
      continue
    if keyword.lower() in thread.name.lower():
      matching.append(thread)

  if matching:
    description = "\n".join(f"- {channel.mention}" for channel in matching)
  else:
    description = "沒有找到包含該關鍵字的討論串。"

  await interaction.followup.send(embed=discord.Embed(
      title=f"搜尋結果 ({keyword})", description=description),
                                  ephemeral=True)


@bot.tree.command(name="list_thread", description="列出任意論壇裡的串文")
@app_commands.describe(channel="論壇")
async def list_thread(interaction: discord.Interaction, channel: ForumChannel):
  await interaction.response.defer(ephemeral=True)
  threads = channel.threads
  description = "\n".join(f"- {channel.mention}" for channel in threads)
  await interaction.followup.send(embed=discord.Embed(title="搜尋結果",
                                                      description=description),
                                  ephemeral=True)


class btnView(discord.ui.View):

  def __init__(self, matching_thread):
    super().__init__(timeout=None)
    self.value = None
    self.matching_thread = matching_thread
    yes_btn = discord.ui.Button(label="是", style=discord.ButtonStyle.green)
    no_btn = discord.ui.Button(label="否", style=discord.ButtonStyle.red)

    async def yes_callback(interaction):
      await self.matching_thread.delete()
      await interaction.response.send_message("串文已刪除", ephemeral=True)

    async def no_callback(interaction):
      await interaction.response.send_message("已取消", ephemeral=True)

    yes_btn.callback = yes_callback
    no_btn.callback = no_callback
    self.add_item(yes_btn)
    self.add_item(no_btn)


@bot.tree.command(name="delete_thread", description="刪除任意論壇裡的串文")
@app_commands.describe(channel="論壇", name="標題")
async def delete_thread(interaction: discord.Interaction,
                        channel: ForumChannel, name: str):
  await interaction.response.defer(ephemeral=True)
  threads = channel.threads

  matching_thread = []
  for thread in threads:
    if thread.name == name:
      matching_thread.append(thread)
      break
  if (len(matching_thread) != 0):
    description = "\n".join(f"- {channel.mention}"
                            for channel in matching_thread)
    await interaction.followup.send(embed=discord.Embed(
        title="確定要刪除此串文嗎?", description=description),
                                    ephemeral=True)

    view = btnView(matching_thread[0])
    await interaction.followup.send(view=view, ephemeral=True)
  else:
    await interaction.followup.send(embed=discord.Embed(
        title="無法找到此串文", color=discord.Color.red()),
                                    ephemeral=True)


@bot.tree.command(name="trend", description="找出任意論壇被提到最多次的關鍵字")
@app_commands.describe(channel="論壇")
async def trend(interaction: discord.Interaction, channel: ForumChannel):
  await interaction.response.defer(ephemeral=True)

  keywords = Counter()

  threads = channel.threads
  for thread in threads:
    words = re.findall(r"\w+", thread.name.lower())  #這網路上查的w

    keywords.update(words)

  sorted_keywords = keywords.most_common()

  i = 0
  description = ""
  for word, count in sorted_keywords:
    i += 1
    description += f"{i}. {word} ({count} 次)\n"
    if i == 3:
      break
  await interaction.followup.send(embed=discord.Embed(title="熱門關鍵字(前三)",
                                                      description=description),
                                  ephemeral=True)


@bot.tree.command(name="edit_thread", description="更改串文標題")
@app_commands.describe(channel="串文所在的論壇", old_title="串文的標題", new_title="新標題")
async def edit_thread(interaction: discord.Interaction,
                      channel: discord.ForumChannel, old_title: str,
                      new_title: str):
  await interaction.response.defer(ephemeral=True)
  thread = discord.utils.get(channel.threads, name=old_title)
  if not thread:
    await interaction.followup.send(f"沒在{channel.mention}中找到串文'{old_title}'",
                                    ephemeral=True)
    return

  if new_title:
    await thread.edit(name=new_title)

  await interaction.followup.send(f"串文成功更新! :D {channel.mention}",
                                  ephemeral=True)


@bot.tree.command(name="random_thread", description="隨機串文")
@app_commands.describe(channel="論壇")
async def random_thread(interaction: discord.Interaction,
                        channel: discord.ForumChannel):
  await interaction.response.defer(ephemeral=True)

  threads = channel.threads

  if not threads:
    await interaction.followup.send(f"在{channel.mention}中沒有找到串文",
                                    ephemeral=True)
    return

  chosen = random.choice(threads)
  await interaction.followup.send(f"隨機串文: {chosen.mention}", ephemeral=True)


# 寫button 要用ui.view class
class calcView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)
    self.x = 0
    self.temp = 0
    self.mode = ""
    self.label_text = "0"
    self.modes = ["add", "minus", "mul", "div"]

    for i in range(1, 10):
      row = (i - 1) // 3 + 1
      btn = discord.ui.Button(label=str(i),
                              style=discord.ButtonStyle.primary,
                              row=row)

      async def btn_callback(interaction: discord.Interaction, num=i):
        await self.input_num(num, interaction)

      btn.callback = btn_callback
      self.add_item(btn)

    btn_clear = discord.ui.Button(label="C",
                                  style=discord.ButtonStyle.danger,
                                  row=0)

    async def clear_callback(interaction):
      self.clear()
      await self.reset(interaction)

    btn_clear.callback = clear_callback
    self.add_item(btn_clear)

    btn_root = discord.ui.Button(label="√",
                                 style=discord.ButtonStyle.secondary,
                                 row=0)

    async def root_callback(interaction):
      await self.root(interaction)

    btn_root.callback = root_callback
    self.add_item(btn_root)

    btn_square = discord.ui.Button(label="x²",
                                   style=discord.ButtonStyle.secondary,
                                   row=0)

    async def square_callback(interaction):
      await self.square(interaction)

    btn_square.callback = square_callback
    self.add_item(btn_square)

    async def rick_callback(interaction):
      await interaction.response.send_message(
          "https://www.youtube.com/watch?v=dQw4w9WgXcQ")  #rick roll hahaha

    btn_rick = discord.ui.Button(label="",
                                 style=discord.ButtonStyle.success,
                                 row=0)
    btn_rick.emoji = "🎁"
    btn_rick.callback = rick_callback
    self.add_item(btn_rick)

    btn_plus = discord.ui.Button(label="+",
                                 style=discord.ButtonStyle.success,
                                 row=1)

    async def plus_callback(interaction):
      await self.add(interaction)

    btn_plus.callback = plus_callback
    self.add_item(btn_plus)

    btn_minus = discord.ui.Button(label="-",
                                  style=discord.ButtonStyle.success,
                                  row=2)

    async def minus_callback(interaction):
      await self.minus(interaction)

    btn_minus.callback = minus_callback
    self.add_item(btn_minus)

    btn_mul = discord.ui.Button(label="*",
                                style=discord.ButtonStyle.success,
                                row=3)

    async def mul_callback(interaction):
      await self.mul(interaction)

    btn_mul.callback = mul_callback
    self.add_item(btn_mul)

    btn_zero = discord.ui.Button(label="0",
                                 style=discord.ButtonStyle.primary,
                                 row=4)

    async def zero_callback(interaction):
      await self.input_num(0, interaction)

    btn_zero.callback = zero_callback
    self.add_item(btn_zero)

    btn_double_zero = discord.ui.Button(label="00",
                                        style=discord.ButtonStyle.primary,
                                        row=4)

    async def double_zero_callback(interaction):
      await self.double_zero(interaction)

    btn_double_zero.callback = double_zero_callback
    self.add_item(btn_double_zero)

    btn_equal = discord.ui.Button(label="=",
                                  style=discord.ButtonStyle.primary,
                                  row=4)

    async def equal_callback(interaction):
      await self.equal(interaction)

    btn_equal.callback = equal_callback
    self.add_item(btn_equal)

    btn_div = discord.ui.Button(label="/",
                                style=discord.ButtonStyle.success,
                                row=4)

    async def div_callback(interaction):
      await self.div(interaction)

    btn_div.callback = div_callback
    self.add_item(btn_div)

  async def input_num(self, num, interaction: discord.Interaction):
    self.x = self.x * 10 + num
    await self.refresh(interaction)

  async def double_zero(self, interaction: discord.Interaction):
    self.x = self.x * 100
    await self.refresh(interaction)

  async def refresh(self, interaction: discord.Interaction):
    self.label_text = str(self.x)
    embed = discord.Embed(title="Calculator",
                          description=self.label_text,
                          color=discord.Color.blurple())
    await interaction.response.edit_message(embed=embed, view=self)

  async def reset(self, interaction: discord.Interaction):
    self.x = 0
    await self.refresh(interaction)

  async def add(self, interaction: discord.Interaction):
    if self.mode == "":
      self.temp = self.x
      self.x = 0
    self.mode = "add"
    await self.refresh(interaction)

  async def minus(self, interaction: discord.Interaction):
    if self.mode == "":
      self.temp = self.x
      self.x = 0
    self.mode = "minus"
    await self.refresh(interaction)

  async def mul(self, interaction: discord.Interaction):
    if self.mode == "":
      self.temp = self.x
      self.x = 0
    self.mode = "mul"
    await self.refresh(interaction)

  async def div(self, interaction: discord.Interaction):
    if self.mode == "":
      self.temp = self.x
      self.x = 0
    self.mode = "div"
    await self.refresh(interaction)

  async def root(self, interaction: discord.Interaction):
    self.x = math.sqrt(self.x)
    await self.refresh(interaction)

  async def square(self, interaction: discord.Interaction):
    self.x = self.x * self.x
    await self.refresh(interaction)

  async def equal(self, interaction: discord.Interaction):
    if self.mode == "add":
      self.x = self.temp + self.x
    elif self.mode == "minus":
      self.x = self.temp - self.x
    elif self.mode == "mul":
      self.x = self.temp * self.x
    elif self.mode == "div":
      self.x = self.temp / self.x
    self.mode = ""
    await self.refresh(interaction)

  def clear(self):
    self.mode = ""
    self.temp = 0

  def isContained(self):
    for m in self.modes:
      if self.mode == m:
        return True
    return False


@bot.tree.command(name="calc", description="計算機")
@app_commands.describe()
async def calc(interaction: discord.Interaction):
  view = calcView()
  embed = discord.Embed(title="Calculator",
                        description=view.label_text,
                        color=discord.Color.blurple())
  await interaction.response.send_message(embed=embed, view=view)


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user}")
  global isOnline
  isOnline["value"] = True
  await bot.tree.sync()
  

def run():
  bot.run(os.getenv("TOKEN"))