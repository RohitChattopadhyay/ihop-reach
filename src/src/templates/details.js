// @flow

import React from "react"
import { Link, graphql } from "gatsby"
import "font-awesome/css/font-awesome.min.css"

import style from "../assets/styles/details.module.scss"
import Layout from "../components/layout"
import Links from "../components/identifierDetails"
import SentenceView from "../components/sentenceView"

export default function DetailsTemplate({ data }) {
  // data = data.ihop.entities.articles // This contains all the articles

  let searchID = data.ihop.documentsByIdentifier.searchkey
  let synonyms = data.mongodbIhopIdentifierMapping.syn
  let entityName = synonyms.reduce((a, b) => (a.length <= b.length ? a : b))
  let entityType = data.mongodbIhopIdentifierMapping.typ
  data = data.ihop.documentsByIdentifier
  return (
    <Layout entity_name={entityName} entity_id={searchID} keywords={synonyms}>
      <div className="container my-4">
        <div>
          <h1 className="display-4 w-100">
            {entityName}
            <span className="lead"> {entityType.split("_").join(" ")}</span>
          </h1>
          <table className={"table " + style.infoTable}>
            <Links
              className={style.detailsLinks}
              data={data.documents}
              identifier={searchID}
              synonyms={synonyms}
            />
          </table>
        </div>
        <div className={style.sentenceContainer}>
          <div className="row">
            <div className="col-sm-11">
              <p className="lead">
                Sentences in this view contain interactions of&nbsp;
                <em>{entityName}</em>
              </p>
            </div>
            <div className="col-sm-1 text-right" title="See how to Interpreting Search Results">
              <a href="/#interpret_result:~:text=Interpreting%20Search%20Results" target="_blank" rel="noopener">
                Help❔
              </a>
            </div>
          </div>
          <SentenceView data={data} identifier={searchID} className={null} />
        </div>
      </div>
    </Layout>
  )
}

export const detailsQuery = graphql`
  query detailsByID($id: String!) {
    ihop {
      documentsByIdentifier(identifier: $id) {
        searchkey
        documents {
          journal_title
          publication_year
          pmc_id
          evidence
          verbose_text
          trigger
          extracted_information {
            participant_a {
              entity_text
              entity_type
              identifier
            }
            participant_b {
              entity_text
              entity_type
              identifier
            }
            hypothesis_information
            negative_information
            context {
              Species
            }
          }
        }
      }
    }
    mongodbIhopIdentifierMapping(iden: { eq: $id }) {
      typ
      syn
    }
  }
`
