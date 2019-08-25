// @flow

import React from "react"

import "font-awesome/css/font-awesome.min.css"

class Links extends React.Component {
  constructor(props) {
    super(props)
  }
  linkParser = identifier => {
    // list of baseURLs
    const baseURL = {
      // [namespace]  : [baseURL, Name of the namespace]
      ["be"]: ["https://github.com/sorgerlab/famplex", "FamPlex"],
      ["chebi"]: ["http://identifiers.org/chebi/", "ChEBI"],
      ["hgnc"]: ["http://identifiers.org/hgnc/", "HGNC"],
      ["hmdb"]: ["http://identifiers.org/hmdb/", "HMDB"],
      ["go"]: ["http://identifiers.org/go/", "GO"],
      ["interpro"]: ["http://identifiers.org/interpro/", "InterPro"],
      ["mesh"]: ["http://identifiers.org/mesh/", "MeSH"],
      ["pfam"]: ["http://identifiers.org/pfam/", "Pfam"],
      ["pubchem"]: ["http://identifiers.org/pubchem.compound/", "PubChem"],
      ["taxonomy"]: ["http://identifiers.org/taxonomy/", "Taxonomy"],
      ["uniprot"]: ["http://identifiers.org/uniprot/", "UniProt"]
    }
    var namespace, id
    var identifierArray = identifier.split(/:(.+)/)
    //splitting the identifier into namespace and id
    namespace = identifierArray[0]
    id = identifierArray[1] // for identifiers with 2 components
    var urlID = namespace === "be" ? "" : id //condition for be namespace
    try {
      var urlNamespace = baseURL[namespace][0] // getting url
    } catch (err) {
      console.log("Missing identifier namespace: ", identifier)
      return null
    }
    // checking url validity
    if (urlNamespace !== undefined || id !== undefined)
      return (
        <tr>
          <td>{baseURL[namespace][1]}</td>
          <td>
            <a href={urlNamespace + urlID} target="_blank">
              {id}
            </a>
          </td>
        </tr>
      )
    else return null
  }
  render() {
    const syn = this.props.synonyms
    return (
      <tbody className={this.props.className}>
        {this.linkParser(this.props.identifier)}
        {syn.length > 1 ? (
          <tr>
            <td>Matches</td>
            <td>{syn.join(", ")}</td>
          </tr>
        ) : null}
      </tbody>
    )
  }
}

export default Links
