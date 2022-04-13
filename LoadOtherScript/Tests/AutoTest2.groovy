import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

pipeline {
    agent any

    stages {
        stage('TestInit') {
            steps {
                // timestamper ver. 1.17
                // 1.18 以降なら timestamps { } を使える
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        test_init(WORKSPACE)
                    }
                }
            }
        }

        stage('Clone') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        clone(WORKSPACE, REPOSITORY_URL, CREDENTIALS_ID, TEST_BRANCH, COMMIT_ID)
                    }
                }
            }
        }

        stage('Execute') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        def date = LocalDateTime.now()
                        def now = date.format(DateTimeFormatter.ofPattern('yyyyMMdd_HHmmss'))
                        if (!execute_test_suite(WORKSPACE, "${now}_${BUILD_ID}")) {
                            error("test failed")
                        }
                    }
                }
            }
        }
    }

    post {
        // 失敗したときは環境確認のためにワークスペースをそのまま残す
        success {
            deleteDir()
        }
    }
}

def test_init(String workspace_path) {
    try {
        println(sh(returnStdout: true, script: "ls -l"))
    } catch (Exception e) {
        println(powershell(returnStdout: true, script: "dir ${workspace_path}"))
    }
}

def clone(String workspace_path, String repository_url, String credentials_id, String branch, String commit_id) {
    dir(workspace_path) {
        clone_core(repository_url, credentials_id, branch, commit_id)
    }
}

def clone_core(String repository_url, String credentials_id, String branch, String commit_id) {
    String branches_name = "refs/heads/${branch}"
    if (commit_id != "") {
        branches_name = commit_id
    }

    checkout_core(repository_url, credentials_id, branches_name)
}

def checkout_core(String repository_url, String credentials_id, String branches_name) {
    println("checkout: ${repository_url} / branches_name: ${branches_name}")
    checkout([
        $class: 'GitSCM', 
        branches: [[name: "${branches_name}"]], 
        doGenerateSubmoduleConfigurations: false, 
        extensions: [[$class: 'CleanCheckout']], 
        submoduleCfg: [], 
        userRemoteConfigs: [[credentials_id: "${credentials_id}",
                             url: "${repository_url}"]]
    ])
}

def execute_test_suite(String workspace_path, String unique_id) {
    def test_MainJobA = load("${workspace_path}/LoadOtherScript/Tests/test_MainJobA2.groovy")
    def common = load("${workspace_path}/LoadOtherScript/Tests/common.groovy")

    def result_test_MainJobA = test_MainJobA.test_suite(workspace_path, unique_id, common)

    if (result_test_MainJobA) {
        return true
    } else {
        return false
    }
}
