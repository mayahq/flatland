(begin
  (define-dag basic
              (
               (define-node plswork loop i 0 5)
               (define-node w1a move 30 0)
               (define-node w1b turn 72)

               (define-node starter loop j 0 360)
               (define-node b1a move (* 10 (sin (/ pi 180))) 1)
               (define-node b1b turn 1)
               (define-node bpost1 turn 54)
               (define-node bpost2 move 25 0)
               
               (link-node plswork:body w1a)
               (link-node w1a w1b)
               (link-node w1b plswork)
               (link-node w1b starter)

               (link-node starter:body b1a)
               (link-node b1a b1b)
               (link-node b1b starter)
               (link-node starter bpost1)
               (link-node bpost1 bpost2)
               )
              )
  (run-dag basic plswork)
)
