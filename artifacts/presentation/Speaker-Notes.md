# Actuarial Signal Radar — speaker notes

Approximately 3 minutes.

## Slide 1

Most dashboards show what happened. Actuarial Signal Radar asks whether it was unusually different from what we would have expected. It turns official insurance data into a signal an analyst can investigate. The separation is deliberate: we detect first, AI investigates second, and humans decide.

## Slide 2

Our source is official CNBS Honduras data for motor insurance in national currency. These are monetary monthly accounting aggregates, not accident or claim counts. March 2025 illustrates the value of asking a better question: the raw ratio was normal, but its deviation from trend and seasonality generated an alert. This is not a validated actuarial loss ratio.

## Slide 3

Using only prior available history, we estimate trend and month-of-year seasonality. Observed minus expected gives a residual. A twelve-month robust z-score checks whether that residual is unusual; other statistics add context. November 2020 remained unscored despite its large spike, because residual history was insufficient. Availability uses a conservative calendar lag, not confirmed release dates.

## Slide 4

In September 2025, reported vehicle claims were about 185.4 million Lempiras. The historical reference was 142.4 million: nearly 43 million, or thirty percent, above expected. The residual robust z-score was 11.02. This is money, not accident counts. Under our lag assumption, the signal becomes available December first. It warrants investigation; it does not establish a cause.

## Slide 5

Detection and investigation are different jobs. Evolus and the AMD-hosted model organize what changed, possible explanations, missing evidence, and useful next checks. Hypotheses remain unestablished. The screenshot is a recorded real public execution in Spanish, not a fresh inference. A human must review every accepted result; AI cannot override the signal.

## Slide 6

Evolus is central to this partner-track submission. Its workflow receives the validated package, retrieves six indexed domain documents with checksum checks, orchestrates AMD Token Factory inference, and validates the response. DeepSeek-V4-Flash completed our tested investigations more reliably than the evaluated Qwen path, not a general benchmark. We did not validate self-hosted ROCm or vLLM. Native semantic search was not independently validated.

## Slide 7

Broad coverage does not mean millions of training examples. This source provides roughly a hundred monthly points per main series. We chose transparent statistics so the same data and configuration produce the same signal. With individual claims, frequency, severity, vehicle characteristics, or repair costs, more complex models could be benchmarked against this baseline. They would not automatically be better.

## Slide 8

The product is public on Cloudflare, backed by Railway, Evolus, and AMD Token Factory. The latest public claims investigation completed in about 154 seconds. The ratio retry exposed an execution-envelope failure; we did not weaken validation. This remains a lagged retrospective backtest, not strict point-in-time performance. Public aggregates, possible revisions, exploratory materiality, and transient runtime state remain limitations. Explore the live demo and source code.