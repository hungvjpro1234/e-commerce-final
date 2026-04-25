# Nexus Shop - Frontend Overview

## Design Decisions

**Nexus Shop** was designed to provide a premium, modern, and clean e-commerce experience while interfacing seamlessly with 6 disjointed microservices operating behind the scenes.

1.  **Architecture**: Next.js App Router was chosen for optimal data-fetching patterns, SEO capabilities, and the built-in Node server capability which acts as an API proxy. 
2.  **API Strategy**: The backend services currently do not have an API gateway and operate on separate Docker ports (`8001-8006`). To solve CORS and authentication complexity, we utilized Next.js Server routes (`/api/[...path]/route.ts`) as a smart reverse proxy. This pattern allows the client to only talk to `/api` while the Next server attaches the tokens and routes it to the specific Django container internally.
3.  **Authentication**: Due to MVP constraints, Authentication checks the token sent back from the `user-service`. The token and basic user data are hydrated into a persistent `Zustand` store utilizing local browser storage (`localStorage`).
4.  **Styling**: The design system relies heavily on `Tailwind CSS`, utilizing a monochromatic aesthetic inspired by Shadcn UI (`Zinc`/`Slate` palettes) focusing heavily on border radiuses, subtle grays, and clear focal CTAs formatted with generic names like `primary` and `destructive`.
5.  **State Management**: Complex mutation boundaries like fetching Product items and Orders are managed efficiently using `Tanstack / React Query`. 
6.  **Responsive Layout**: Handled dynamically utilizing `flex` and `grid` systems ensuring the UI works as perfectly on Mobile browsers as Desktops.

## Key Screenshots / Flow

1.  **Login/Register Flow**: User securely attempts to login, if no user exists, creates an account passing `first_name` and `last_name`. This hits `/auth/register` and `/auth/login`. 
2.  **Product List**: Landing page pulls items from `/products/`. Generates Unsplash stock images as placeholders for aesthetics dynamically mapped by category.
3.  **Product Detail**: Dynamic specs render depending on category (e.g. `Author` for books, `Warranty` for electronics).
4.  **Cart Summary**: Updates the Cart Item via `/cart/update` and deletes via `/cart/remove`.
5.  **Checkout Flow**: Checkout prompts for an Address and provides a specific flag (`Simulate Payment Failure`) to rigorously test the `payment-service` and `order-service` rollback mechanisms without jumping into code.
6.  **Tracking Dashboard**: Order tracking resolves the `General Status`, `Payment Status`, and `Shipping Pipeline` from 3 different microservices dynamically using React Query mapping.
