(begin
  (define-dag basic
              (
               (define-node starter loop qq 0 360) 
               (define-node b1a move (* 10 (sin (/ pi 180))) 0)
               (define-node b1b turn 1)
               (define-node bpost move 25 0)
               
               (link-node starter bpost)
               (link-node starter b1a)
               (link-node b1a b1b)
               (link-node b1b starter)
               )
              )
  (run-dag basic starter)
)
