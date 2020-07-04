// @flow

import React from "react"
import { Helmet } from "react-helmet"

const Head = ({ entity_name, entity_id, keywords }) => {
  const title_String = (entity_name?(`${entity_name} (${entity_id}): Article Snippets: `):"") + "iHOP Reach"
  return <Helmet>
    <meta charSet="utf-8" />
    <title>{title_String}</title>
    <meta name="keywords" content={`REACH, iHOP , ` + (keywords && keywords.join(", "))} />
  </Helmet>
}

export default Head
