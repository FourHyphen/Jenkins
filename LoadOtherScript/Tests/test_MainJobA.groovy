def test_suite(def workspace_path) {
    // 多分ここ: java.nio.file.NoSuchFileException: C:\ProgramData\Jenkins\.jenkins\workspace\LoadOtherScript\MainJobA.groovy
    // 現在地はここのはず: C:\ProgramData\Jenkins\.jenkins\workspace\LoadOtherScript\AutoTest
    script_MainJobA = load_script("${workspace_path}/LoadOtherScript/MainJobA.groovy")

    // println("execute: pre_process()")
    // script_MainJobA.pre_process()
    // println("executed: pre_process()")

    return true
}

def load_script(def load_script_path) {
    def script = load load_script_path
    println("loaded")
    return script
}

return this
