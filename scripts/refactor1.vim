let @m=':s#for \w\+ in range(\([0-9]\+\)):#self._dealNumRows(\1)#jdd'
map <F2> /^    def startGame(self):\n        self\._startAndDealRowAndCards()<CR>2dd?^class<CR>:s/(/(pysollib.game.StartDealRowAndCards, /<CR>
