## Frontend Setup & Execution

The frontend has been constructed utilizing Next.js 14 and Tailwind CSS and is capable of running alongside the microservices. 

It implements an internal server-side API Gateway to route to the individual microservice ports.

### Prerequisites (If running locally instead of Docker)

- Node.js 18+

### Environment Configuration

In the `frontend/` directory, create a `.env.development` file pointing to `localhost` ports if you are running the backend microservices using raw python directly on the host machine. Otherwise, `.env.production` is mapped to the internal Docker domain names naturally if running via Docker Compose.

```env
USER_SERVICE_URL=http://user-service:8002
PRODUCT_SERVICE_URL=http://product-service:8001
CART_SERVICE_URL=http://cart-service:8003
ORDER_SERVICE_URL=http://order-service:8004
PAYMENT_SERVICE_URL=http://payment-service:8005
SHIPPING_SERVICE_URL=http://shipping-service:8006
```

### Starting the Frontend with Docker Compose

An added service definition `frontend` mapped to port `3000` has been appended to the root `docker-compose.yml`. 

Simply execute from the root directory:

```bash
docker compose up --build
```

Then visit [http://localhost:3000](http://localhost:3000)

### Manual Local Startup 

If you prefer to start the frontend completely independent of Docker for faster iterative UI development:

```bash
cd frontend
npm install
npm run dev
```

The server will be hosted on [http://localhost:3000](http://localhost:3000). Ensure the other 6 Python apps are actively running so the Next.js Proxy (`/api/...`) resolves properly.

## Important Backend Assumptions
- We assume standard JWT responses where User Service returns `{ access: "...", user: {...} }` upon Authentication.
- In `CartItem`, the cart response maps `product_id` which the frontend actively resolves iteratively against Product Service endpoints.
- Due to the nature of the MVP, `product images` are simulated client-side via Unsplash utilizing deterministic seed sequences to ensure aesthetically cohesive demonstrations.
