orchestral_tutti_chord_database
===============================

.. image:: https://img.shields.io/pypi/v/orchestral_tutti_chord_database.svg
    :target: https://pypi.python.org/pypi/orchestral_tutti_chord_database
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/RCJacH/orchestral_tutti_chord_database.png
   :target: https://travis-ci.org/RCJacH/orchestral_tutti_chord_database
   :alt: Latest Travis CI build status

Introduction
------------

Orchestral Tutti Chord Database, as its name suggests, is a project to collect and to analyze the balance of tutti chords in orchestral settings. Tutti chords are chords played by the whole orchestra, or a large part of the orchestra, usually the sustained chord at the beginning or the end of a piece. Because these chords have weak melodic or motivic connection to the actual music, if any at all, they are perfect as a reference for learning how to balance different orchestral sections.


Method of Analysis
------------------

The method for analyzing balance is by collecting all notes played by each instrument from the woodwind, brass, and string sections (keyboard and percussion omitted currently), place them together onto one single grand staff, and calculate the weight of each note on each octave. Because there is a difference in resonance between sections, a balance ratio is used for calculation. Currently we are using the ratio described in `Rimsky-Korsakov's Principle of Orchestration <https://imslp.org/wiki/Principles_of_Orchestration_(Rimsky-Korsakov,_Nikolay>`_, listed below:

Forte:
  * One string section, i.e. Violin I = 2.
  * One woodwind instrument, i.e. Flute 1 = 1.
  * One Horn or one saxophone = 2.
  * One brass instrument, i.e. Trumpet 1 = 4.

Piano:
  * One string section == one woodwind == one horn == one brass == 1.


Note:
Perhaps a more elaborated and accurately calculated resonance balancing method can be incorporated into this analysis.


Database
--------

The actual database for each piece will be a json file with the following information:

Piece:

  * Composer
  * Year
  * Opus number
  * part/movement
  * measure
  * Tempo
  * Orchestra size
  * Audio link
  * Performer
  * Score link
  * IMSLP link
  * Chord symbol

Chord:

  * Sections

    * Instruments

      * Clef
      * Pitches
      * Accent
      * Dynamic
      * Technique

The json file is generated automatically by the script included, based on manual input in plain text. The library will analyze the music and create a result score page using lilypond.


Score
-----


#To Be Updated


Authors
-------

`orchestral_tutti_chord_database` was written by `RCJacH <RCJacH@outlook.com>`_.
