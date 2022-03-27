pipeline {
    agent any

    stages {
        stage('Env') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        echo ("ParamString: " + ParamString)
                        echo ("ParamText: " + ParamText)

                        // これでちゃんと bool 扱いになってる
                        if (ParamBool) {
                            echo ("ParamBool(True): " + ParamBool)
                        } else {
                            echo ("ParamBool(False): " + ParamBool)
                        }
                    }
                }
            }
        }
    }
}
