# Third-party files

`imports/` holds local copies of the ontologies RBACO-BFO imports, so that it opens and checks without network access (`catalog-v001.xml` resolves the imports to them). They are not covered by `LICENSE.md`.

| Files | What | Source | License |
|---|---|---|---|
| `imports/bfo-core.ttl` | BFO 2020 core, by the contributors the file names; unmodified | https://github.com/bfo-ontology/bfo-2020 (version IRI `http://purl.obolibrary.org/obo/bfo/2020/bfo-core.ttl`) | CC BY 4.0, stated in the file |
| `imports/bfo-clif/*.cl` (13) | The BFO 2020 axiomatization in CLIF, generated 2025-12-05, by Alan Ruttenberg; unmodified | https://github.com/bfo-ontology/bfo-2020 | CC BY 4.0, stated in each file |
| `imports/AgentOntology.ttl`, `ArtifactOntology.ttl`, `EventOntology.ttl`, `ExtendedRelationOntology.ttl`, `GeospatialOntology.ttl`, `InformationEntityOntology.ttl`, `TimeOntology.ttl` | Seven modules of the Common Core Ontologies, version 2.2 (version IRIs dated 2026-08-13); unmodified | https://github.com/CommonCoreOntology/CommonCoreOntologies | BSD 3-Clause, Copyright (c) 2017, CUBRC, INC; the license text is below |
| `imports/iao-extract.ttl` | An extract of the Information Artifact Ontology, release 2026-03-30; modified, see below | http://purl.obolibrary.org/obo/iao/2026-03-30/iao.owl | CC BY 4.0, stated in the file |

`imports/SHA256SUMS` and `imports/bfo-clif/SHA256SUMS` hold the hashes of the unmodified copies.

**Changes to IAO.** `imports/iao-extract.ttl` is generated, not copied. `tools/build_iao_extract.py` keeps, for each IAO term RBACO-BFO uses, its declaration, label, definition, domain and range, and every subclass axiom whose signature lies within those terms and BFO 2020 core, and it drops the rest of IAO. The script prints every subclass axiom it drops; from the 2026-03-30 release it drops two, both on IAO_0000104 (plan specification). The file names its source and license in its own header.

## CCO license

```text
BSD 3-Clause License

Copyright (c) 2017, CUBRC, INC

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## Not included

The checks use tools that are not in this repository: ROBOT and HermiT (`robot.jar`), and Prover9, Mace4 and clausetester from LADR. `docs/expected-results.md` says where each comes from. The three papers RBACO-BFO is built from are not included either (`sources/README.md`).
