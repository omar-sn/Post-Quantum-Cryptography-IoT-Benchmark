#set rect(
  width: 100%,
  height: 100%,
  inset: 4pt,
)
#let title-page(title:[], emails:array, group:[], members: array, body) = {
  set page(margin: (top: 1.5in, rest: 2in))
  set text(size: 16pt)
  set heading(numbering: "1.1.1")
  line(start: (0%, 0%), end: (8.5in, 0%), stroke: (thickness: 2pt))
  align(horizon + left)[
    #text(size: 24pt, title)\
    #v(1em)
    Post Quantum Cryptography on Raspberry Pi
    #v(1em)
    #for email in emails [
      #link("mailto:" + email, email)
      #linebreak()
    ]
    #v(1em)
    Group: #group
    #v(1em)
    Group Members:
    #linebreak()
    #members.join(", ") 
  ]
  
  align(bottom + left)[#datetime.today().display()]
  pagebreak()
  set page(fill: none, margin: auto)
  align(horizon, outline(indent: auto))
  pagebreak()
  body
}

#show: body => title-page(
  title: [Informatik Projekt 2],
  emails:(
    "12mojo1bif@hft-stuttgart.de", 
    "22alay1bif@hft-stuttgart.de",
    "12haombif@hft-stuttgart.de"
  ),
  group: "4",
  members: (
    "Jonas Möwes", "Ayham Alhasan", "Omar Haj Abdulaziz" 
  ),
  body
)
#set text(size: 11pt)

#counter(page).update(1)
#set page(
  numbering: "1",
  number-align: center,
)

#include "sections/Intro.typ"

#include "sections/Realisation.typ"

#include "sections/Data.typ"

#include "sections/Further_Details.typ"


= Evaluation

= Conclusion

