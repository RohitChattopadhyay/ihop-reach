// @flow

import React from "react"
import Header from "./header"
import Footer from "./footer"
import Head from "./head"
import "../assets/styles/customization.scss"

import LayoutStyles from "../assets/styles/layout.module.scss"

const Layout = props => {
  return (
    <div className={LayoutStyles.container}>
      <Head entity_name={props.entity_name} entity_id={props.entity_id} keywords={props.keywords} />
      <div className={LayoutStyles.content}>
        <Header />
        <div className={"container"}>{props.children}</div>
      </div>
      <Footer />
    </div>
  )
}

export default Layout
