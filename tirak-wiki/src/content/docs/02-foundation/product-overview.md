---
title: Product Overview
description: Current Tirak marketplace definition, roles, taxonomy, and booking flow.
category: foundation
order: 1
icon: package
lastUpdated: 2026-07-18
---

# Tirak Product Overview

## Product Definition

Tirak is a Thailand travel marketplace where travelers discover and book named guided cultural activities delivered by verified local guides. Examples include a Chinatown food walk, an Ayutthaya temple route, a market-and-cooking experience, a neighborhood architecture walk, or a museum-led history itinerary.

Tirak is not a dating, companionship, escort, adult-services, romantic matching, or social-discovery app. It does not sell a person's time, availability, company, or affection.

## The Purchasable Unit

Every bookable item is a **guided experience** and must include:

- A descriptive activity title and category
- A summary of the cultural or travel outcome
- A defined itinerary or route
- Location and meeting point
- Date, start time, and duration
- Group size and accessibility information
- Included and excluded items
- Total experience price in THB
- Cancellation and refund terms
- The responsible local guide and their credentials

A guide profile may show identity verification, languages, qualifications, experience history, reviews, and the experiences they lead. The guide profile is supporting trust information; it is not independently bookable.

## Roles

### Traveler

Browses experiences, requests a dated itinerary, pays Tirak after confirmation, receives booking updates, coordinates logistics within the booking, and reviews the delivered travel service.

### Local Guide

Publishes or is assigned to structured experiences, confirms itinerary availability, coordinates meeting logistics, delivers the listed activity, and receives an approved marketplace payout outside the traveler checkout surface.

### Tirak

Defines marketplace standards, reviews listings and guides, holds the booking record, collects the experience payment, provides safety/reporting tools, communicates status, and manages support and refund cases.

## Supported Categories

- Culture and heritage
- Food and drink tours
- Markets and neighborhoods
- Cooking and craft workshops
- Nature and outdoor activities
- Wellness activities with a defined service provider and itinerary
- Arts, museums, and architecture
- Family-friendly activities
- Ticketed local events when clearly described

`Private` is retired as a category. “Private group” may describe an attendance format only when it means the customer books a defined experience exclusively for their own party; it must never describe discreet, intimate, adult, or one-to-one company.

## Booking State Machine

1. `draft`: the traveler selects an experience and supplies booking details.
2. `pending`: Tirak persists the request; no payment is available.
3. `confirmed`: the guide accepts the itinerary and date; checkout becomes available.
4. `payment_pending`: Tirak creates a booking-bound PromptPay charge.
5. `paid`: Tirak independently verifies successful payment with Omise.
6. `completed`: the guided experience was delivered.

Declined, cancelled, expired, and failed-payment states must be explicit. A failed or expired payment does not delete the booking and can be retried only while the booking remains confirmed.

## Communication Boundary

Chat exists only inside a persisted booking and is limited to travel logistics such as the meeting point, timing, accessibility, dietary needs, language preference, group details, and itinerary clarifications. Profiles do not expose a general-purpose chat invitation.

## Payment Boundary

PromptPay pays Tirak for a confirmed, real-world guided travel experience. Tirak derives the amount from the server-side booking. The mobile app never sends card data, secret keys, or a user-selected amount. This payment rail must not purchase subscriptions or digital feature unlocks.

## Release Metrics

- Confirmed guided-experience bookings
- Booking-to-payment completion
- Guide acceptance time
- Experience completion rate
- Safety reports per completed booking
- Refund and cancellation rate
- Traveler rating of the delivered itinerary

Downloads, profile views, time spent in chat, or person-to-person matches are not primary product outcomes.
