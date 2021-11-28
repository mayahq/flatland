(begin
  (define-dag basic
              (
               (define-node starter loop 0 360) 
               (define-node b1 move (* 10 (sin (/ pi 180))) 1)
               (define-node bpost move 25 0)
               
               (link-node starter bpost)
               (link-node starter b1)
               (link-node b1 starter)
               )
              )
  (run-dag basic starter)
)
