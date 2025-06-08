enum ProcessType {
    Emulation,
    OnBoard
}

// ただ load するだけだと参照不可。enum を load 先で参照する仕掛け
//  -> このファイルを複数 load されると 2 重定義エラーになるので注意が必要
this.ProcessType = ProcessType

return this
