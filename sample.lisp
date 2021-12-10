(begin
  (define-flow basic (pmove)
              (
               (create-node starter loop qq 0 360) 
               (create-node b1a move (* 10 (sin (/ pi 180))) 0)
               (create-node b1b turn 1)
               (create-node bpost move pmove 0)
               
               (create-entry starter)
               
               (create-link starter bpost)
               (create-link starter:body b1a)
               (create-link b1a b1b)
               (create-link b1b starter)

               (create-exit starter)
               )
              )
  (run-flow basic (20) (64 54) 0)
)
