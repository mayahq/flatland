(begin
  (define-dag basic
              (
               (define-node starter loop 0 360 ())
               (define-node b1 move (* 10 (sin (/ tau 360))) 1 ())
               
               (link-node starter b1)
               )
              )
  (run-dag basic starter)
)
