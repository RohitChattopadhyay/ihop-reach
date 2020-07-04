// @flow

import React from "react"
import { Cookies } from "react-cookie"
import style from "../assets/styles/sentenceView.module.scss"
type Props = {
  data: Object,
  className: string,
}

class SentenceView extends React.Component<Props> {
  constructor() {
    super()
    this.state = {
      allSentences: [],
      displayRes: [],
      pmc: null,
      hypo: null,
      negInfo: null,
      human: false,
      search: null,
      year: null,
      title: null,
      sentence: null
    }
  }
  highlighter = (sentence: string, data: Object, identifier: string) => {
    const color = {
      celltype: "#e9b54d",
      cellular_component: "#85b6d8",
      family: "#7a1199",
      gene_or_gene_product: "#445e2b",
      organ: "#fc751b",
      protein: "#0000ff",
      simple_chemical: "#cf7d8a",
      site: "#85b6d8",
      species: "#15407a",
      trigger: "inherit",
      current: "red",
    }
    let terms = []
    let entityText, entityColor, entityType, replacement
    //trigger
    if (data.trigger != undefined) {
      terms.push({
        text: data.trigger,
        color: color["trigger"],
        type: "Trigger",
      })
    }

    //participants
    const participantA = data.extracted_information.participant_a
    const participantB = data.extracted_information.participant_b
    const participants = Array.from(
      new Set(participantA.concat(...participantB))
    )
    if (participants.length == 0) return null
    participants.forEach(participant => {
      if (
        !(participant.entity_text) ||
        !(participant.entity_type) ||
        !(participant.identifier)
      )
        return

      entityText = participant.entity_text
      entityType = participant.entity_type.split("_").join(" ")
      if (participant.identifier == identifier) {
        entityColor = color["current"]
        entityType = "Current"
      } else entityColor = color[participant.entity_type]
      terms.push({
        text: entityText,
        color: entityColor,
        type: entityType,
        identifier: participant.identifier,
      })
    })
    terms.forEach(word => {
      if (
        word.type != "Current" &&
        word.type != "Trigger" &&
        word.identifier.search(new RegExp("uazid", "i")) < 0
      )
        replacement = `<a target="_blank" href="./${word.identifier}" style="color:${word.color}" title="${word.type}"><b><u>${word.text}</u></b></a>`
      else
        replacement = `<span style="cursor:default; color:${word.color}" title="${word.type}"><b>${word.text}</b></span>`
      sentence = sentence.replace(word.text, replacement)
    })
    return sentence
  }

  filterFunction = obj => {
    const { pmc, hypo, negInfo, speciesInfo, search, year, title, sentence } = this.state
    let regx_pmc = new RegExp(pmc, "i")
    let regx_year = new RegExp(year, "i")
    let regx_title = new RegExp(title, "i")
    let regx_sentence = new RegExp(sentence, "i")
    return (
      (pmc != null ? obj.pmcid.search(regx_pmc) > -1 : true) &&
      (speciesInfo != null ? obj.species == speciesInfo : true) &&
      (year != null
        ? obj.year.search(regx_year) > -1
        : true) &&
      (title != null
        ? obj.title.search(regx_title) > -1
        : true) &&
      (sentence != null
        ? obj.sentence.search(regx_sentence) > -1
        : true) &&
      (hypo != null ? obj.hypothesis === hypo : true) &&
      (negInfo != null ? obj.negInfo === negInfo : true)
    )
  }
  handleFilter = () => {
    const { pmc, hypo, negInfo, speciesInfo, title, sentence, year } = this.refs
    try {
      let regx_pmc = new RegExp(pmc.value, "i")
      let regx_year = new RegExp(year.value, "i")
      let regx_title = new RegExp(title.value, "i")
      let regx_sentence = new RegExp(sentence.value, "i")
    } catch (e) {
      window.alert(`${e.name}\n${e.message}`)
      return
    }
    this.setState({
      pmc: pmc.value.length > 1 ? pmc.value : null,
      speciesInfo: speciesInfo.value == "0" ? null : speciesInfo.value,
      title: title.value.length > 2 ? title.value : null,
      sentence: sentence.value.length > 2 ? sentence.value : null,
      year: year.value.length > 1 ? year.value : null,
      hypo: hypo.value == "0" ? null : hypo.value == "2" ? true : false,
      negInfo:
        negInfo.value == "0" ? null : negInfo.value == "2" ? true : false,
    })
  }

  generateTextFragment = text => {
    // Populate text fragment in Full Text search for PMC journal
    var searchText = "";
    var words = [];
    var temp_words = text.split(" ");
    for (var idx = 0; idx < temp_words.length; idx++) {
      if (!temp_words[idx].includes("XREF"))
        words.push(temp_words[idx]);
    }
    if (words.length < 7)
      searchText = encodeURIComponent(text);
    else {
      for (var idx = 0; idx < 6 && idx < words.length; idx++) {
        searchText += " " + encodeURIComponent(words[idx]);
      }
      var secondLastWord = "";
      if (words.length > 7)
        secondLastWord = words[words.length - 2] + " ";
      var lastWord = words[words.length - 1];
      if (lastWord.endsWith("."))
        lastWord = lastWord.substring(0, lastWord.length - 1)
      searchText += "," + encodeURIComponent(secondLastWord + lastWord);
    }
    return searchText.trim()
  }

  getOrgFromTaxonomy = identifier => {
    let name = "",
      abv = " "
    let blank = true
    if (identifier != null && identifier.length > 0) {
      switch (identifier[0]) {
        case "taxonomy:9606":
          // Human
          abv = "Hs\u00A0\u00A0"
          name = "Human"
          blank = false
          break
        case "taxonomy:10090":
          // Mouse
          abv = "Mm"
          name = "Mouse"
          blank = false
          break
        case "taxonomy:4932":
          // Yeast
          abv = "Sc\u00A0\u00A0"
          name = "Yeast"
          blank = false
          break
        case "taxonomy:10116":
          // Rat
          abv = "Rn\u00A0\u00A0"
          name = "Rat"
          blank = false
          break
        default:
          abv = " "
          name = ""
          break
      }
    }
    if (blank)
      return (
        <small className="invisible">{"Mm"}</small>
      )
    else
      return (
        <small style={{ cursor: "default" }} title={"Organism: " + name}>
          {abv}
        </small>
      )
  }
  render() {
    const documents = this.props.data.documents
    const identifier = this.props.identifier
    var array = []
    let highlightedHTML
    documents.map(document => {
      //Fallback for verbose_text
      let sentArray = [];
      if ("verbose_text" in document) {
        if (document.verbose_text != null && document.verbose_text.length > 2)
          sentArray.push(document.verbose_text)
        else
          sentArray = document.evidence
      }
      else
        sentArray = document.evidence

      return sentArray.map(sentence => {
        highlightedHTML = this.highlighter(sentence, document, identifier)
        if (highlightedHTML == null || sentence.length < 50) return
        let species
        try {
          species = document.extracted_information.context.Species
        } catch {
          species = null
        }
        array.push({
          hypothesis: document.extracted_information.hypothesis_information,
          negInfo: document.extracted_information.negative_information,
          species: species,
          sentence: sentence,
          pmcid: document.pmc_id,
          year: document.publication_year,
          title: document.journal_title,
          html: highlightedHTML,
        })
      })
    })
    let htmlArray = []
    let unique = array.filter((item, pos) => {
      if (htmlArray.indexOf(item.html) == -1) {
        htmlArray.push(item.html)
        return true
      } else return false
    })

    if (unique.length === 0) {
      return <p style={{ textAlign: "center" }}>No Sentence Found</p>
    }
    let dispArr = unique.filter(this.filterFunction)
    return (
      <table className="w-100">
        <thead>
          <tr>
            <td colSpan="5">
              <div className="form-row my-auto">
                <div className="col-2 col-sm-2">
                  <input
                    className="form-control form-control-sm"
                    type="text"
                    placeholder="PMC ID"
                    ref="pmc"
                    onChange={this.handleFilter}
                  />
                </div>
                <div className="col-sm-2 col-3">
                  <select
                    className="form-control form-control-sm"
                    ref="hypo"
                    onChange={this.handleFilter}
                  >
                    <option hidden value="0">
                      Hypothesis Information
                    </option>
                    <optgroup label="Hypothesis Information">
                      <option value="2">True</option>
                      <option value="1">False</option>
                      <option value="0">All</option>
                    </optgroup>
                  </select>
                </div>
                <div className="col-sm-2 col-4">
                  <select
                    className="form-control form-control-sm"
                    ref="negInfo"
                    onChange={this.handleFilter}
                  >
                    <option hidden value="0">
                      Negative Information
                    </option>
                    <optgroup label="Negative Information">
                      <option value="2">True</option>
                      <option value="1">False</option>
                      <option value="0">All</option>
                    </optgroup>
                  </select>
                </div>
                <div className="col-sm-1 col-3">
                  <select
                    className="form-control form-control-sm"
                    ref="speciesInfo"
                    onChange={this.handleFilter}
                  >
                    <option hidden value="0">
                      Species
                    </option>
                    <optgroup label="Species">
                      <option value="taxonomy:9606">Human</option>
                      <option value="taxonomy:10090">Mouse</option>
                      <option value="taxonomy:4932">Yeast</option>
                      <option value="taxonomy:10116">Rat</option>
                      <option value="0">All</option>
                    </optgroup>
                  </select>
                </div>
                <div className="col-sm-5 form-row">
                  <div className="col">
                    <input
                      className="form-control form-control-sm"
                      type="text"
                      placeholder="Sentence Search"
                      ref="sentence"
                      onChange={this.handleFilter}
                    />
                  </div>
                  <div className="col">
                    <input
                      className="form-control form-control-sm"
                      type="text"
                      placeholder="Journal Search"
                      ref="title"
                      onChange={this.handleFilter}
                    />
                  </div>
                  <div className="col">
                    <input
                      className="form-control form-control-sm"
                      type="number"
                      placeholder="Year search"
                      ref="year"
                      onChange={this.handleFilter}
                    />
                  </div>
                </div>
              </div>
            </td>
          </tr> 
          {dispArr.length > 0 && (
            <tr className={[style.tableHeader,"border-top","pt-4"].join(" ")}>
              <th></th>
              <th>
                <div className="row">
                  <div className="col-sm-9 text-center">Sentence</div>
                  <div className="col-sm-3">Journal Title</div>
                </div>
              </th>
              <th title="Publication Year">
                <div className="row">
                  <div className="col-12">Year</div>
                </div>
              </th>
            </tr>
          )
          }     
        </thead>
        <tbody
          className={[this.props.className, style.sentenceTable, "w-100"].join(" ")}
        >
          {dispArr.length == 0 ? (
            <tr>
              <th>No Results Found, please refine your filter.</th>
            </tr>
          ) : (
              dispArr.map(obj => {
                return (
                  <tr key={obj.html}>
                    <th className="d-none d-sm-inline">
                      <a
                        title="Link to Full-Text Article"
                        href={`https://www.ncbi.nlm.nih.gov/pmc/articles/PMC${
                          obj.pmcid
                          }#:~:text=${this.generateTextFragment(obj.sentence)}`}
                        target="_blank"
                        rel="noopener"
                      >
                        <i className="fa fa-file-text-o" aria-hidden="true" />
                      </a>
                    </th>
                    <th className="d-none d-sm-inline">
                      {obj.hypothesis ? (
                        <i
                          title="Hypothetical Statement Suggesting Interaction"
                          className="fa fa-star-half-o"
                          aria-hidden="true"
                        />
                      ) : (
                          <i
                            className="fa fa-star invisible"
                            aria-hidden="true"
                          />
                        )}
                    </th>
                    <th className="d-none d-sm-inline">
                      {obj.negInfo ? (
                        <i
                          title="Statement Suggesting Absence of an Interaction"
                          className="fa fa-minus-circle"
                        />
                      ) : (
                          <i className="fa fa-minus-circle invisible" />
                        )}
                    </th>
                    <th className="d-none d-sm-inline">
                      {this.getOrgFromTaxonomy(obj.species)}
                    </th>
                    <td>
                      <div className="row">
                        <div className={"d-sm-none col-12 " + style.mobileSentenceView} >
                          <span>
                            <a
                              title="Link to Full-Text Article"
                              href={`https://www.ncbi.nlm.nih.gov/pmc/articles/PMC${
                                obj.pmcid
                                }#:~:text=${this.generateTextFragment(obj.sentence)}`}
                              target="_blank"
                              rel="noopener"
                            >
                              <i className="fa fa-file-text-o" aria-hidden="true" />
                            </a>
                          </span>
                          {obj.hypothesis ? (
                            <span>
                              <i
                                title="Hypothetical Statement Suggesting Interaction"
                                className="fa fa-star-half-o"
                                aria-hidden="true"
                              />
                            </span>
                          ) : ""}
                          {obj.negInfo ? (
                            <span>
                              <i
                                title="Statement Suggesting Absence of an Interaction"
                                className="fa fa-minus-circle"
                              />
                            </span>
                          ) : ""}
                          <span>
                            {this.getOrgFromTaxonomy(obj.species)}
                          </span>
                        </div>
                        <div
                          className="col-sm-9"
                          dangerouslySetInnerHTML={{
                            __html: obj.html,
                          }}
                        />
                        <div className="col-sm-3"><em>{obj.title}</em><small className="d-sm-none">{obj.year.length > 0 ? (", " + obj.year) : ""}<hr /></small></div>

                      </div>
                    </td>
                    <th className="d-none d-sm-inline ">{obj.year}</th>
                  </tr>
                )
              })
            )}
        </tbody>
        {/* PAGINATION HAS BEEN SKIPPED DUE TO LOW NUMBER OF SENTENCES */}
        <tfoot className="invisible">
          <tr>
            <td colSpan="2">
              <div className="mt-2 w-100">
                <ul className="pagination pagination-sm float-right">
                  <li className="page-item disabled">
                    <span className="page-link">
                      <i className="fa fa-chevron-left" />
                    </span>
                  </li>
                  <li className="page-item active">
                    <span className="page-link" href="#">
                      1
                    </span>
                  </li>
                  <li className="page-item">
                    <span className="page-link" href="#">
                      2
                    </span>
                  </li>
                  <li className="page-item">
                    <a className="page-link" href="#">
                      3
                    </a>
                  </li>
                  <li className="page-item">
                    <a className="page-link" href="#">
                      4
                    </a>
                  </li>
                  <li className="page-item">
                    <a className="page-link" href="#">
                      5
                    </a>
                  </li>
                  <li className="page-item">
                    <span className="page-link">
                      <i className="fa fa-chevron-right" />
                    </span>
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        </tfoot>
      </table>
    )
  }
}

export default SentenceView
