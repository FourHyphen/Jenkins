pipeline {
    agent any

    stages {
        stage('file test') {
            steps {
                script {
                    test_file()
                }
            }
        }
    }
}

def test_file() {
    // node 1 つ追加したら master ノードに割り当てられなくなった
    // node("master") {
    //     echo("---- master node ---------------------------------")
    //     test_file_core()
    // }

    node("centos7") {
        echo("---- centos7 node ---------------------------------")
        test_file_core()
    }
}

def test_file_core() {
    String work_dir_path = "/mnt/c/MyDevelopment/GitHub/Jenkins/sjis"
    String utf_8_file = "${work_dir_path}/utf-8.groovy"
    String sjis_file = "${work_dir_path}/sjis.groovy"

    ///////////////////////////////////////////////////
    // master ノード
    //     単純な echo        -> 文字化けなし
    //     utf-8 ファイル cat -> 文字化け
    //     sjis ファイル cat  -> 文字化けなし
    //
    //     /etc/locale.conf -> ファイルなし
    //     環境変数 LANG     -> LANG=C.UTF-8
    ///////////////////////////////////////////////////

    ///////////////////////////////////////////////////
    // centos7 初期設定
    //     単純な echo        -> 文字化けなし
    //     utf-8 ファイル cat -> 文字化け
    //     sjis ファイル cat  -> 文字化け
    //
    //     /etc/locale.conf -> LANG="en_US.UTF-8"
    //     環境変数 LANG     -> なし
    ///////////////////////////////////////////////////

    echo("そもそも Jenkins として日本語表示できるかをここで確認")
    echo("---------------------------------------")

    echo("locale 確認")
    sh(script: "locale -a")
    sh(script: "locale")
    echo("---------------------------------------")

    try {
        echo("utf_8_file: ${utf_8_file}")
        sh(script: "cat ${utf_8_file}")

        echo("utf_8_file cat > redirect")
        sh(script: "cat ${utf_8_file} > ${utf_8_file}_cat_redirect.txt")

        echo("utf_8_file load")
        def tmp1 = load(utf_8_file)
        tmp1.test_utf_8()
    } catch (Exception e) {
        echo("${e}")
        echo("utf_8_file のどこかで失敗")
    }
    echo("---------------------------------------")

    try {
        echo("sjis_file: ${sjis_file}")
        sh(script: "cat ${sjis_file}")

        echo("sjis_file cat > redirect")
        sh(script: "cat ${sjis_file} > ${sjis_file}_cat_redirect.txt")

        echo("sjis_file load")
        def tmp2 = load(sjis_file)
        tmp2.test_utf_8()
    } catch (Exception e) {
        echo("${e}")
        echo("sjis_file のどこかで失敗")
    }
}
