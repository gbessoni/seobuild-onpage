# Schema Markup Patterns

JSON-LD schema markup templates for each page type. The skill generates
these at the end of each page as a code block.

## FAQPage (use on any page with an FAQ section)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here."
      }
    }
  ]
}
```

## LocalBusiness (service + location pages)

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Business Name",
  "description": "What the business does",
  "url": "https://example.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "City",
    "addressRegion": "ST",
    "postalCode": "12345",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "priceRange": "$$"
}
```

## HowTo (guide/tutorial pages)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [action]",
  "description": "Brief description",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step title",
      "text": "Step description"
    }
  ]
}
```

## Product (product/feature pages)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "brand": {
    "@type": "Brand",
    "name": "Brand Name"
  },
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "9.99",
    "highPrice": "99.99",
    "priceCurrency": "USD"
  }
}
```

## BreadcrumbList (all pages, especially location hierarchies)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Category",
      "item": "https://example.com/category/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Current Page"
    }
  ]
}
```

## Combination Patterns

Most pages should combine multiple schemas. Common combos:

- **Service page:** LocalBusiness + FAQPage + BreadcrumbList
- **Comparison page:** FAQPage + BreadcrumbList
- **How-to page:** HowTo + FAQPage + BreadcrumbList
- **Location page:** LocalBusiness + FAQPage + BreadcrumbList
- **Product page:** Product + FAQPage + BreadcrumbList

When combining, wrap in an array:

```json
[
  { "@context": "https://schema.org", "@type": "FAQPage", ... },
  { "@context": "https://schema.org", "@type": "BreadcrumbList", ... }
]
```

## Validation

Always validate generated schema at:
- https://search.google.com/test/rich-results
- https://validator.schema.org/

---

## Inline RDFa / Microdata (required since v1.8.0)

JSON-LD in `<head>` is necessary but no longer sufficient. Google's AI Overview
pipeline extracts structural "shards" from the rendered DOM, so critical data
must also be visible to a clean-session crawler in the body. Pair every JSON-LD
block with front-facing markup: real `<table>` elements, or inline RDFa spans.

### Entity + price

```html
<p vocab="https://schema.org/" typeof="Product">
  <span property="name">JFK Long-Term Lot 9</span> charges
  <span property="offers" typeof="Offer">
    <span property="price">20.00</span>
    <span property="priceCurrency" content="USD">USD</span>
  </span> per day.
</p>
```

### Place + operating detail

```html
<span vocab="https://schema.org/" typeof="ParkingFacility">
  <span property="name">Lot 9</span> holds
  <span property="maximumAttendeeCapacity">8500</span> vehicles.
</span>
```

### Microdata alternative

```html
<div itemscope itemtype="https://schema.org/LocalBusiness">
  <span itemprop="name">SmartPark JFK</span>
  <span itemprop="telephone">+1-718-555-0100</span>
  <span itemprop="openingHours" content="Mo-Su 00:00-23:59">Open 24/7</span>
</div>
```

### Rules

- Critical pricing, capacity, schedule, and location data appears in the body,
  not only in a `<head>` script tag.
- Tabular data uses real `<table>` markup. Never simulate a table with bullets.
- The inline markup must describe content the human actually sees. Do not add
  RDFa to hidden text.
- Numbers inside these blocks are still subject to `{{VERIFY}}` tagging.
