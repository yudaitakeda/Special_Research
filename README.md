# Spetial_Research
もしすでに push してしまっている場合は、リモートリポジトリの状態を元に戻すために、次の手順を実行します。

git reset --hard HEAD~1  # ローカルで1つ前のコミットに戻す
git push -f origin ブランチ名  # 強制的にリモートを上書き
