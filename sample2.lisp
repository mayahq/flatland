(begin
  (define-dag basic
              (
               (define-node plswork loop 0 5 ())
               (define-node t0 turn 72 ())
               (define-node w1 move 30 ())

               (define-node starter loop 0 360 ())
               (define-node b1 move (* 10 (sin (/ tau 360))) ())
               (define-node b2 turn 1 ())
               
               (link-node plswork t0)
               (link-node t0 starter)
               (link-node t0 w1)
               (link-node starter b1)
               (link-node b1 b2)
               )
              )
  (run-dag basic plswork)
)
