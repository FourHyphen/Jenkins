class DataA {
    string name
    int age
}

def stage_a(DataA data) {
    println("stage_a.groovy: stage_a()")
    println(data.name)
    println(data.age)
}

return this
