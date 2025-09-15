def test_utf_8() {
    String str = """#!/bin/bash
echo "このファイルは SJIS です"
echo "日本語が表示されるかテスト"
"""
    echo(str)
}

return this
