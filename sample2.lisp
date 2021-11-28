(begin
  (define-dag basic
              (
               (define-node plswork loop 0 5)
               (define-node w1 move 30 72)

               (define-node starter loop 0 360)
               (define-node b1 move (* 10 (sin (/ pi 180))) 1)
               (define-node bpost move 20 162)
               
               (link-node plswork w1)
               (link-node w1 plswork)
               (link-node w1 starter)

               (link-node starter b1)
               (link-node b1 starter)
               (link-node starter bpost)
               )
              )
  (run-dag basic plswork)
)
