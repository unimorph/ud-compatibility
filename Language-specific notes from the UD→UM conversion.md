# Language-specific notes from the UD→UM conversion

## Encoding issues

Some languages had a very low number of overlapping forms, and no tag matches or near-matches between them: Arabic, Hindi, Persian, Lithuanian. Slovenian also had very few, but it was workable.

## Latvian
Noun genders, as always...

Our annotations of past participles are tragically different.

Many verbs are ambiguous about 3rd-person SG/PL. Shouldn't we use a disjunction? UD just refuses to mark number.

UniMorph LOC tag shouldn't exist. We don't acknowledge a locative case; ESS is a close match.

We don't mark ACT, FIN, POS, or FH evidentiality on verbs.

We don't mark POS on infinitives, but we mark NEG.
FORM	UD converted	UniMorph options
turēt	NFIN;POS;V	['NEG;NFIN;V', 'NFIN;V']   

## Basque

We don't conform to our own template style for arguments. ARGABS3;ARGABSSG;IND;PRES;V should be ARGAB3S;IND;PRES;V. My script labels with *correct* UniMorph, not what's present.

We also lack a way to encode the politeness of the argument.

## Bulgarian
We mark case; they mark gender. Nothing we can do there.

UD treats IPFV as some default on verbs, like ACT and FIN. We never mark either, so *shrug*.

They treat "ACT" as an implicit default for participles.

We mark a bunch of ADJs as ACC or NOM where UD has no case.

Some UD verbs are impoverished in terms of tense.

## Catalan
Why are we using colons as separators instead of only  semicolons?

We should be marking IPFV for the imperfect subjunctive. For now, I'm stripping that out of UD to optimize harmony over accuracy, while still not allowing *wrong* tags to enter bundles.

UD labels a bunch of infinitives as PROPN.

They also mark a lot of present subjunctive as past subjunctive.

## Czech

There's a surfeit of data for Czech, but so much of it is not agreeing with UniMorph. I find myself mostly hacking off details that we left out, rather than trying to make matches in the way that I would for Spanish.

## Danish
We mark case; they mark gender. Nothing we can do there.

For verbs, this the only language I've seen us mark participles as passive. UD does it for a lot of languages, but not this one.

## Dutch

The level of tagging in UD is extremely impoverished compared to UniMorph. Since I'm not going to manually annotate each ambiguous case to say whether it's 1st, 2nd, or 3rd person, for instance, I have to punt here.

## English

The only things I couldn't harmonize in good conscience were (1) the helper verbs (e.g. will, can) that were annotated as only "V", and (2) the imperatives.

## Finnish
What is "GEADJ"? I believe it's supposed to be "GEN".             

## Hungarian

We disagree on the POS of so many words. We say N, they say ADJ. Hard to marry beyond that. They have imperatives. We don't. Also, why do we have an INST tag? It should be INS. I'm largely convinced that our nouns are labeled wrong.

## Irish
We mark case; they mark gender. Nothing we can do there.

## Italian

This is more of a general mark: we handle imperatives in Romance languages very poorly. I don't think they're attested in UniMorph.

So many words UD labels as PST;V.PTCP that aren't. 



## Lithuanian
UniMorph INST should be INS. As is frequent, UniMorph doesn't mark ACT and FIN.

## Norwegian Bokmål
Why do we have NDEF instead of the spec's INDF?

## Norwegian Nynorsk
Same problem. Also participles are underspecified.

## Romanian

Romanian has a neuter gender that looks masculine in singular and feminine in plural. No UD-ro words were tagged as neuter. UniMorph doesn't acknowledge that adjectives applied to, e.g. feminine and neuter-plural 

The UniMorph annotations for Romanian have a number of problems. (1) They omit braces in feature disjunctions, e.g. {NOM/ACC}. (2) Number on nouns is consistently wrong.

Romanian noun tables seem to be incomplete, because I keep seeing instances of UD aligning with my understanding of Romanian.

Disagreement between masdar and converb.
