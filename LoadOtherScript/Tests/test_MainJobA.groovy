def test_suite() {
    script_MainJobA = load_script("../MainJobA.groovy")

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
