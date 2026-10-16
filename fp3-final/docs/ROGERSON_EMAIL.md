# Contribution / question emails to Prof. Ken Rogerson

**To:** rogerson@duke.edu
Each author sends their **own** email from their **own DKU account**. The two are
deliberately different: different contribution, different question. Do not send both from
one account, and do not send them as a single joint email.

**No attachment is required.** The assignment asks only for the introduction, the specific
thanks, your own contribution and one question. The repository link in the signature is
sufficient, and each email offers to send the paper or poster if he wants them.

After sending, record the date in `appendices/supporting.tex` (search `ROGERSON`).

---

## Email 1 — Feiyu Li

**Subject:** COMSCI/ECON 206 — a better answer to your question at the September 7 workshop

Dear Professor Rogerson,

I am Feiyu Li, an undergraduate at Duke Kunshan University taking COMSCI/ECON 206
Computational Microeconomics with Professor Luyao Zhang. With my teammate Xuantong Fu I
form Team FP3.

At the 2056 Nobel and Turing Laureate Program Launch Workshop on 7 September, where you
served as Program Discussant, you asked us what made our AI better than the AI that came
before it. I answered that it would be more accurate. I am writing because six weeks of
building it have convinced me that was the wrong answer, and I would like to give you a
better one.

Our system scores a company's disclosure; investors act on that score, so it affects how
much capital the company raises; capital changes the company's later performance; and that
performance becomes training data for the same system. Its evidence about its own accuracy
is therefore partly a record of its own past decisions. Such a system looks *more* accurate
on its own backtest exactly as it becomes less trustworthy, so accuracy was the one
statistic it can inflate by itself.

My own contribution was to argue that what settles this is not the model but the market
mechanism around it: only a shock that changes how much a firm raises, without changing
what the firm said, can separate the system's influence from genuine quality. I rebuilt our
IPO auction so bids genuinely compete for scarce shares, and verified that 16 of 50
investors are now excluded and a bid below the clearing price receives nothing. That
produced a result we had not anticipated — when the system learns naively from its own
outcomes, inflated scores compress bids until the auction stops sorting at all, so the
failure appears as *who gets financed* rather than as mispricing.

So my answer now is that our system is not better at predicting. It is better at knowing
when it is not entitled to learn, and it freezes itself when it cannot verify that.

My question is about that freeze, because it is a public act: it announces that an
evaluator has temporarily lost the standing to certify itself. In your experience of how
public institutions and their audiences actually behave, does a visible self-declared pause
build credibility over time, or does it create enough pressure that institutions quietly
avoid ever declaring one?

I would be glad to send the two-page paper or the poster if either would be useful; I have
not attached anything so as not to presume on your time.

Thank you for the question. It was the most useful thing anyone asked us this semester.

With respect,
**Feiyu Li**
Duke Kunshan University · COMSCI/ECON 206, Prof. Luyao Zhang · Team FP3
github.com/dku-comsci-econ206-Autumn2026/ps2-fp3

---

## Email 2 — Xuantong Fu

**Subject:** COMSCI/ECON 206 — following up on your question at the September 7 workshop

Dear Professor Rogerson,

I am Xuantong Fu, an undergraduate at Duke Kunshan University taking COMSCI/ECON 206
Computational Microeconomics with Professor Luyao Zhang. My teammate is Feiyu Li; we are
Team FP3.

At the 2056 Nobel and Turing Laureate Program Launch Workshop on 7 September, where you
served as Program Discussant, you asked what made our AI better than the AI that preceded
it. We answered in terms of accuracy. Our project has since become, in effect, an argument
that the honest answer is a different kind of claim: our system is not a better predictor,
it is one that can tell when it has lost the right to update itself.

My contribution was to decide what that test should be, and then to show our first version
of it was broken. The system is allowed to revise its own rule only while a statistic
confirms that its own influence is separable from the evidence it learns from. I found that
the version of that statistic in our earlier draft had been computed incorrectly — divided
by the wrong quantity — which made a correction that actually works appear useless. I then
ran the test I had publicly challenged our own team with: if a stronger shock still
produced a weak statistic, our whole correction would be worthless. It did not. But I also
found that below the threshold our corrected estimator does not merely become biased, it
becomes erratic, with an error roughly nine times the safeguarded version's worst case.
That is why our system refuses to update rather than updating cautiously when it cannot
verify itself.

My question concerns publishing that threshold. We borrowed it from a standard
econometric convention, which means it is public and therefore a target: anyone who
benefits from the evaluator staying frozen has an incentive to suppress the very variation
the test needs. When a public institution must publish the standard by which it judges
itself, what usually keeps that standard from becoming the thing people manage rather than
meet?

I have not attached anything, but I would be happy to send the paper or the poster if
either would be useful to you.

Thank you for your time, and for a question that turned out to shape the whole project.

With respect,
**Xuantong Fu**
Duke Kunshan University · COMSCI/ECON 206, Prof. Luyao Zhang · Team FP3
github.com/dku-comsci-econ206-Autumn2026/ps2-fp3
