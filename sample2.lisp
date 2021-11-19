(begin
  (define-dag basic
              (
               (define-node plswork loop 0 5 ())
               (define-node w1 move 30 72 ())

               (define-node starter loop 0 360 ())
               (define-node b1 move (* 10 (sin (/ tau 360))) 1 ())
               
               (link-node plswork starter)
               (link-node plswork w1)
               (link-node starter b1)
               )
              )
  (run-dag basic plswork)
)
