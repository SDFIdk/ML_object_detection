# [Eksperiment: Firkant-arealer](https://github.com/Kortforsyningen/[INDSÆT-ARKIV-ID])

Dette eksperiment laver data, der kan bruges til at illustrere, hvordan arealet af en firkant vokser med sidelængderne på firkanten.

## Systemkrav

For at anvende programmet, skal du have følgende installeret, samt have mulighed for at køre det fra en system-terminal:

*   Git til at hente programmet
*   SSH til overførsel af data mellem lokal versionshistorik og centralt arkiv på GitHub
*   Python 3.10.0+


## Installation

*   Hent koden:

    ```sh
    git clone https://github.com/Kortforsyningen/[INDSÆT-ARKIV-ID]
    ```

## Eksempel på anvendelse

*   Gå til mappen `scripts` i roden af arkivet:

    ```sh
    cd template-python-prototype/scripts
    ```
    
*   Beregn areal med fire sidelængder:

    ```sh
    python run.py 1 2 3 4
    # Resultat
    # {
    #   "sides": {
    #     "a": 1.0,
    #     "b": 2.0,
    #     "c": 3.0,
    #     "d": 4.0
    #   },
    #   "area": 4.898979485566356
    # }
    ```

## Bidrag til dette arkiv

*   Konkrete ønsker kan oprettes som [GitHub issues](https://github.com/Kortforsyningen/[INDSÆT-ARKIV-ID]/issues).

*   Bidrag kan oprettes gennem GitHubs forking- og pull-request-mekanisme:
    -   På kodearkivets side, vælg Fork
    -   Fra din egen fork, lav en by branch og foretag rettelserne i denne.
    -   Når du er klar, kan du oprette et pull-request fra den nye branch.
