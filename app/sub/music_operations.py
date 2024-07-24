# music_operations.py

import discord
import asyncio


# 音楽再生
async def play(ctx):
    # ボイスチャンネルに接続
    if ctx.author.voice is None:
        await ctx.send("まず、ボイスチャンネルに参加してください。")
        return
    # 発言者の入っているボイチャ特定
    channel = ctx.author.voice.channel
    # BOT入室
    if ctx.voice_client is None:
        vc = await channel.connect()
    else:
        vc = ctx.voice_client
    # ループ再生
    for i in range(11):
        # 音楽を再生
        audio_source = discord.FFmpegPCMAudio(source="./music/loop_music.mp3")
        vc.play(audio_source, after=lambda e: asyncio.create_task(handle_playback_error(ctx, e)))
        # 再生が終了するまで待機
        while vc.is_playing():
            await asyncio.sleep(1)
        # 再生終了後にボイスチャンネルから切断
    await vc.disconnect()
    await ctx.send("再生終了につき、ボイスチャンネルから切断しました。")


# 音楽停止
async def stop(ctx):
    if ctx.voice_client:
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()  # 再生中の音楽を停止
            await ctx.voice_client.disconnect()
            await ctx.send("ボイスチャンネルから切断しました。")
        except Exception as e:
            await ctx.send(f"ボイスチャンネルからの切断中にエラーが発生しました: {e}")
    else:
        await ctx.send("ボイスチャンネルに入ってません！")


# 再生エラー処理
async def handle_playback_error(ctx, error):
    if error:
        await ctx.send(f'音楽の再生中にエラーが発生しました: {error}')
