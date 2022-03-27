DO_STAGE = [
    'DO_STAGE_ENV':false,
    'DO_STAGE_TIMEOUT':false,
    'DO_STAGE_OTHERJOB':false,
    'DO_STAGE_WAITUNTIL':false,
    'DO_STAGE_SAVEARTIFACTS':true,
    'DO_STAGE_FINDARTIFACTS':false,
    'DO_STAGE_META':true,
    'DUMMY':false    // コピペが楽になるように
]

pipeline {
    agent any

    stages {
        stage('Env') {
            when {
                allOf {
                    // expression: 中で true 返したときだけ実行
                    expression {
                        return DO_STAGE['DO_STAGE_ENV']
                    }
                }
            }
            steps {
                // timestamper ver. 1.17
                // 1.18 以降なら timestamps { } を使える
                wrap([$class: 'TimestamperBuildWrapper']) {
                    // 変数定義等、あらゆることをするには script ブロックが必要
                    script {
                        env.getEnvironment().each {
                            out_console(it.toString())
                        }
                    }
                }
            }
        }

        stage('Timeout') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_TIMEOUT'] } } }
            steps {
                // 分 -> unit:'MINUTES'
                timeout(time: 5, unit: 'DAYS') {
                    echo "Timeout block."
                }
            }
        }

        stage('OtherJob') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_OTHERJOB'] } } }
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        parallel(
                            "CallOtherJob": {
                                build(job: 'OtherJob',
                                   // parameters: [text(name: 'OUTPUT_TEXT', value: 'hoge hoge')])
                                      parameters: [[$class: 'StringParameterValue', name: 'ParamString', value: 'ParamStringHoge'],
                                                   [$class: 'TextParameterValue', name: 'ParamText', value: 'ParamTextHoge'],
                                                   [$class: 'BooleanParameterValue', name: 'ParamBool', value: true]])
                            }
                        )
                    }
                }
            }
        }

        // 参考: https://qiita.com/miyasakura_/items/9d9a8873c333cb9e9f43
        stage('WaitUntil') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_WAITUNTIL'] } } }
            steps {
                script {
                    // 戻り値が true になるまでループ
                    waitUntil {
                        try {
                            echo "waitUntil { }"
                            true  //いらないかも
                        } catch(error) {
                            sh "sleep 30"
                            false
                        }
                    }
                }
            }
        }

        // 参考: https://qiita.com/ys1230415/items/51b36fedf1434e877765
        // ファイルをビルド成果物として実行結果に登録できる
        stage('SaveArtifacts') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_SAVEARTIFACTS'] } } }
            steps {
                script {
                    def fileName = "output.txt"
                    def textStr = "output"
                    writeFile(file: fileName, text: textStr)
                    archiveArtifacts(fileName)
                }
            }
        }

        // 他ジョブの成果物を取得する
        stage('FindArtifacts') {
            // 常に失敗するので常にスキップさせる
            when { allOf { expression { return false } } }
            steps {
                script {
                    copyArtifacts(projectName: "他ジョブ名")

                    // No such DSL method 'findFiles'
                    files = findFiles(glob: '*.*')
                    files.each {
                        echo ("artifact: " + it)
                    }
                }
            }
        }

        stage('Meta') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_META'] } } }
            steps {
                script {
                    String.metaClass.methods.each {
                        method -> println(method)
                    }
                }
            }
        }
    } // stages

    // stages 終了後
    post {
        // これまでが成功なら
        success {
            // ワークスペースを真っ新にする
            cleanWs()
            echo "post: success: succeeded."
        }
    }
}

def out_console(String str) {
    echo "${str}"
}

