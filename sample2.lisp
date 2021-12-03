(begin
  (define-flow circle (radius)
               (
                (create-node starter loop j 0 360)
                (create-node b1a move (* radius (sin (/ pi 180))) 0)
                (create-node b1b turn 1)

                (create-entry starter)
                (create-link starter:body b1a)
                (create-link b1a b1b)
                (create-link b1b starter)
                (create-exit starter:out out)
                )
               )
  (define-flow basic ()
               (
                (create-node plswork loop i 0 5)
                (create-node w1a move 30 0)
                (create-node w1b turn 72)

                (create-node starter circle 10)
                (create-node bpost1 circle 5)
                (create-node bpost1b turn 54)
                (create-node bpost2 move 25 0)

                (create-entry plswork)
                (create-link plswork:body w1a)
                (create-link w1a w1b)
                (create-link w1b plswork)
                (create-link w1b starter)

                (create-link starter bpost1)
                (create-link bpost1 bpost1b)
                (create-link bpost1b bpost2)

                (create-exit plswork)
                )
               )
  (run-flow basic () (49 39) 0)
  )
