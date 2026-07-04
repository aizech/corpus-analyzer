"""About page for Corpus Analyzer."""

import streamlit as st

from ui import render_page_header


def main():
    render_page_header(
        "About",
        subtitle="by Corpus Analytica",
        page_icon="material/info",
    )

    st.markdown("""
# Corpus Analyzer Overview

Corpus Analyzer is a cutting-edge medical AI platform that delivers intelligent diagnostics, image analysis, and research insights through a secure, intuitive interface built for healthcare professionals and patients alike.

## Key Features

- **Intelligent Diagnostics**: Advanced AI-powered analysis for accurate medical interpretations
- **Image Analysis**: Comprehensive medical image processing and interpretation
- **Research Insights**: Access to medical literature and research databases
- **Secure Platform**: Enterprise-grade security for patient data protection

## Why Choose Corpus Analyzer?

Corpus Analyzer stands at the forefront of medical AI innovation, combining cutting-edge technology with clinical expertise to deliver unparalleled healthcare solutions. Our platform is designed to empower both healthcare providers and patients with intelligent tools that enhance decision-making and improve outcomes.

## Our Mission

To revolutionize healthcare delivery through intelligent AI-powered tools that enhance diagnostic accuracy, improve patient outcomes, and make expert medical insights accessible to all.

# Corpus Analytica - Your Trusted Partner in Healthcare

At [Corpus Analytica](https://www.corpusanalytica.com), we redefine how medical professionals and patients connect—through a platform built for simplicity, security, and global reach.

#### What We Offer:
- Seamless Connections: We unite doctors, specialists, and patients through our cutting-edge digital platform.

- Expert Second Opinions: Gain easy access to a network of certified physicians and specialists for reliable second opinions.

- Effortless Booking: Our intuitive interface makes requesting and scheduling consultations fast and frustration-free.

- Global Access: Wherever you are, our online consultations bring expert medical advice right to your screen.

- Data You Can Trust: We uphold the highest standards in data protection and patient privacy—because your health deserves nothing less.

#### Experience Healthcare in a New Dimension
Your health is invaluable. With Corpus Analytica, discover a smarter, safer, and more connected way to care.

> *"Healthcare should be accessible, transparent, and empowering. At Corpus Analytica, we're building more than just a platform—we're building trust, one consultation at a time."* — Bernhard Z., Founder of [Corpus Analytica](https://www.corpusanalytica.com)

""")


main()
