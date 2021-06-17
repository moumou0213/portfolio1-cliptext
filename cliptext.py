import time
import datetime
import pyperclip
import webbrowser
from word_processor import word_processor
import re
import csv
import argparse
import os

# コマンドライン引数の解析を行う
# -f と -n の２つのオプションを用意する
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--false", action="store_true",
                    help="Google Imageの自動検索を行わない")
parser.add_argument("-n", "--filename",
                    help="ファイル名を指定する。"
                         "指定しなかった場合はプログラム実行時の時間がファイル名になる。")
args = parser.parse_args()


# Google Imageの検索に用いるベースとなるURL
base_url = 'https://www.google.com/search?tbm=isch&q='

# Google Imageで単語を自動検索するか否かについて
# もしコマンドライン引数で -f または --false が指定された場合は自動検索を行わない
GoogleImage = True
# -f または --false というオプションを指定した場合
if args.false:
    GoogleImage = False


# ファイル名をどうするかについて
# -n または --filename のオプションでファイル名が指定された場合
if args.filename:
    # 指定された文字列がそのままファイル名になる
    filename = args.filename
else:
    # オプションでファイル名が指定されなかった時
    # 現在の時刻からファイル名を作成する
    now = datetime.datetime.now()
    filename = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}'

# 出力のテキストファイルが保存されるフォルダの名前はoutputとする
# outputフォルダの中に作成したテキストファイルが全て保存される
# 初めてこのコードを実行した場合のみ、outputフォルダを作成する
dirname = 'output'
if not os.path.exists(dirname):
    os.mkdir(dirname)
abspath = dirname + '/' + filename


# SVL12000の辞書を作成する
# キーが英単語でバリューがその単語のレベルである
with open('data/svl12000.csv', encoding='utf-8-sig') as f:
    rows = csv.reader(f)
    list_svl12000 = [row for row in rows]
# リストから辞書を作成する
dict_svl12000 = dict(list_svl12000)


# クリップボードを空にする
pyperclip.copy('')
# １つ前のクリップボードの中身を空に初期化する
pre_clipboard = ''


try:
    while True:
        # 現在のクリップボードの中身は now_clipboard で管理する
        now_clipboard = pyperclip.paste()

        # もしもクリップボードの中身が更新されていたらファイルに内容を追記する
        # もしもクリップボードの中身が更新されていたらその単語をGoogle Imageで検索する
        if now_clipboard != pre_clipboard:
            # 現在のクリップボードの内容を変数wordにコピーする
            # Google Imageで検索するために加工するのはwordのみ。now_clipboardはそのまま。
            word = now_clipboard
            word = word_processor(word)

            # wordが１つの英単語であるときに限ってGoogle Imageで検索する
            # wordが１つの英単語であるときに限ってSVL12000におけるレベルを検索し、
            # ファイルに書き込む時に英単語の横にそのレベルを表示させる
            match = re.match(r'^[-’a-zA-Z]+$', word)
            if match:
                # Google Imageの自動検索をするか否かは変数GoogleImageで決定する
                if GoogleImage:
                    # Google ImageのベースとなるURLと検索したい単語を元にURLを作成する
                    url = base_url + word
                    # 合成したURLを用いてブラウザを開く
                    webbrowser.open(url)

                # 英単語のレベルをSVL12000で検索してその情報を単語の横に書き込む
                with open(abspath, mode='a') as f:
                    # ファイルに書き込むのはnow_clipboardであって加工済みのwordではない
                    # 最初の改行の直後に単語のレベルを書き込む
                    temp_list = now_clipboard.split(sep='\n', maxsplit=1)
                    temp_list[0] += f'  <{dict_svl12000.get(word, "-")}>'
                    f.write('\n'.join(temp_list))
                    f.write('\n')
                    # ファイルに書き込んだ内容と同じ内容をコンソールにも出力する
                    print('\n'.join(temp_list))
            else:
                # コピーした内容が１つの英単語でない場合はその内容をそのままファイルに追記する
                with open(abspath, mode='a') as f:
                    f.write(now_clipboard)
                    f.write('\n')
                    # ファイルに書き込んだ内容と同じ内容をコンソールにも出力する
                    print(now_clipboard)


            # １つ前のクリップボードの中身を更新する
            pre_clipboard = now_clipboard

        time.sleep(1)
except KeyboardInterrupt:
    # ユーザーが Ctrl+C を押すとプログラムを終了する
    print('プログラムを終了しました。')
