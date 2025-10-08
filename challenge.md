# FDE Take-Home Exercise: Creative Automation for Social Campaigns

---

Please plan to spend **6–8 hours** on the overall assignment. Complete deliverables described in **all three tasks** and be prepared to share what you have created in a **30-minute presentation**.

**Required:** Record a quick demo of the exercise working to help the interviewers set up/run the app locally for review. You will be asked to send the presentation and recording to your Talent Partner **the day before your scheduled interview**.

## Scenario: Creative Automation for Scalable Social Ad Campaigns

**Client:** A global consumer goods company launching hundreds of localized social ad campaigns monthly.

### Business Goals

1. **Accelerate campaign velocity:** Rapidly ideate, produce, approve, and launch more campaigns per month to drive localized engagement and conversion.
2. **Ensure brand consistency:** Maintain global brand guidelines and voice across all markets and languages.
3. **Maximize relevance & personalization:** Adapt messaging, offers, and creative to resonate with local cultures, trends, and consumer preferences.
4. **Optimize marketing ROI:** Increase campaign efficiency by improving performance and top-line growth (CTR, conversions) versus cost and efficiencies (both time and spend).
5. **Gain actionable insights:** Track effectiveness at scale and learn what content/creative/localization drives the best business outcomes.

### Pain Points

1. **Manual content creation overload:** Creating and localizing variants for hundreds of campaigns per month is slow, expensive, and error-prone.
2. **Inconsistent quality & messaging:** Risk of off-brand or low-quality creative due to decentralized processes and agencies.
3. **Slow approval cycles:** Bottlenecks in review/approval with multiple stakeholders in each region and market.
4. **Difficulty analyzing performance at scale:** Siloed data and manual reporting hinder learning and optimization.
5. **Resource drain:** Skilled creative and marketing teams are overloaded with repetitive requests versus value-driving work.

---

## Objective

Design a creative automation pipeline that enables the creative team to generate variations for campaign assets.

### Data Sources

* **User inputs:** Campaign briefs and assets uploaded manually.
* **Storage:** Save generated or transient assets (can be **Azure**, **AWS**, or **Dropbox**).
* **GenAI:** Best-fit APIs available for generating hero images, resized and localized variations.

---

## Task 1: Create a High-Level Architecture Diagram and Roadmap

**Architecture Diagram** — Detailed architecture diagram for the overall content pipeline.

**Roadmap** — High-level roadmap (1 slide) to show the overall delivery timelines and epics.

**Stakeholders**

* Creative Lead
* Ad Operations
* IT
* Legal/Compliance

**System Architecture**

* Asset ingestion
* Storage
* GenAI-based asset generation

**Deliverables**

* High-Level Architecture Diagram
* Roadmap (1 slide)

---

## Task 2: Build a Creative Automation Pipeline (Proof of Concept)

**Goal:** Demonstrate a working proof-of-concept that automates creative asset generation for social ad campaigns using GenAI. The implementation should show your technical approach, problem-solving, and ability to integrate creative technologies.

### Requirements (minimum)

* Accept a **campaign brief** (in JSON, YAML, or other reasonable format) with:

  * Product(s) — at least two different products
  * Target region/market
  * Target audience
  * Campaign message
* Accept **input assets** (local folder or mock storage) and reuse them when available.
* When assets are missing, **generate new ones** using a GenAI image model.
* Produce creatives for at least **three aspect ratios** (e.g., **1:1, 9:16, 16:9**).
* **Display the campaign message** on the final campaign posts (English at least; localized is a plus).
* **Run locally** (command-line tool or simple local app; your choice of language/framework).
* **Save generated outputs** to a folder, clearly organized by product and aspect ratio.
* Include **basic documentation (README)** explaining:

  * How to run it
  * Example input and output
  * Key design decisions
  * Any assumptions or limitations

### Nice to Have (optional for bonus points)

* **Brand compliance checks** (e.g., presence of logo, use of brand colors)
* **Simple legal content checks** (e.g., flagging prohibited words)
* **Logging or reporting** of results

> Please ensure that your solution reflects thoughtful design choices and demonstrates a clear understanding of the code. These aspects will be part of the evaluation.

---

## Task 3: Create an Agentic System Design & Stakeholder Communication

**Design an AI-driven agent to:**

* Monitor incoming campaign briefs.
* Trigger automated generation tasks.
* Track the count and diversity of creative variants.
* Flag missing or insufficient assets (e.g., fewer than 3 variants).
* Provide an alert and/or logging mechanism.

**Model Context Protocol:** Define the information the LLM sees to draft human-readable alerts.

**Sample Stakeholder Communication:** Compose an email to customer leadership explaining delays (e.g., due to GenAI API provisioning or licensing issues).

---

## Deliverables

Please share the following deliverables for each task described above:

1. **Task 1:** Prepare a 30-minute presentation including:

   * A high-level Roadmap and Approach
   * A backend and data integration design
2. **Task 2:** A public GitHub repository containing:

   * The creative automation pipeline code
   * A comprehensive README file
3. **Task 3:** Design an AI-Driven Agent and share:

   * Agentic System Design
   * Email — Stakeholder Communication
