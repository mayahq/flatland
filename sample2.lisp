(begin
  (define-dag basic
              (
               (define-node plswork loop 0 5 ())
               (define-node w1 move 30 72 ())

               (define-node starter loop 0 360 ())
               (define-node t1 turn 10 ())
               (define-node b1 move (* 10 (sin (/ pi 180))) 1 ())
               
               (link-node plswork w1)
               (link-node w1 starter)
               (link-node starter t1)
               (link-node t1 b1)
               )
              )
  (run-dag basic plswork)
)
