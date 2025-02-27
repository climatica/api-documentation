# Geocoding

Our API's geocoding directly leverages [Google's Geocoding API](https://developers.google.com/maps/documentation/geocoding/overview). It is provided as a best-effort convenience. For the most accurate results, please geocode addresses prior and request analysis results using verified lat/lon pairs. Google's Geocoding data and/or matching algorithm changes without notice & can be responsible for apparent changes in analysis results.

# Geocoding Quality

Google's Geocoding API provides two main dimensions to assess quality:
- the match
- the location type

For **matching**, we have a few data points:
- number of results returned
- `partial` flag
- address component breakdown

For **location type** there are 4 possible values (in order from most to least precise):
1. ROOFTOP
2. RANGE_INTERPOLATED
3. GEOMETRIC_CENTER
4. APPROXIMATE

## Our Handling

We only ever use the first result, but use the number of results returned as a signal of match accuracy.

Location type ROOFTOP
- If there's only 1 match and it's not marked as partial, the quality is `good`.
- If it was marked as partial, the quality is `usable`.
- If there was more than 1 result, the quality is `impreciseMatch`.

Location type RANGE_INTERPOLATED
- If there's only 1 match and it's not marked as partial, the quality is `impreciseLocation`.
- If it was marked as partial, the quality is `impreciseLocation`.
- If there was more than 1 result, the quality is `impreciseMatch`.

If the location type is either of GEOMETRIC_CENTER or APPROXIMATE, this means the location is the centroid of something like an entire suburb, state, or country - not useful & potentially misleading. The geocoding quality is marked as `bad` and no results will be returned.

We have chosen not to use the component breakdown at this time because different components feature more prominently in different areas of the world so it's not really possible to arrive at a single solution that works globally. We can revisit this in time if need be.
