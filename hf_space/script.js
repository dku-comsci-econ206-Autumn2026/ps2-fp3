/* ============================================================
   AI VALUATION & STRATEGIC DISCLOSURE GAME
   PS2 Computational Microeconomics

   Research structure:

   Firm
      ↓
   Strategic disclosure
      ↓
   AI evaluator
      ↓
   AI valuation
      ↓
   Investor private signal
      ↓
   First-price allocation
      ↓
   Capital
      ↓
   Firm performance
      ↓
   AI historical learning

   ============================================================ */


/* ============================================================
   GLOBAL PARAMETERS
   ============================================================ */

const GAME_CONFIG = {

    rounds: 6,

    maxQuality: 100,

    manipulationCostCoefficient: 0.08,

    capitalProductivity: 0.25,

    signalNoise: 8,

    valuationNoise: 3,

    competitorNoise: 10,

    baseCapital: 40,

    maxCapital: 100

};


/* ============================================================
   GAME STATE
   ============================================================ */

let game = {

    role: null,

    round: 1,

    memoryMode: "static",

    history: [],

    current: null,

    totalUtility: 0,

    totalProfit: 0,

    totalManipulation: 0,

    totalAIError: 0,

    totalAllocation: 0

};


/* ============================================================
   RANDOM HELPERS
   ============================================================ */

function randomNormal(mean = 0, std = 1) {

    let u = 0;
    let v = 0;

    while (u === 0) {
        u = Math.random();
    }

    while (v === 0) {
        v = Math.random();
    }

    const z =
        Math.sqrt(-2.0 * Math.log(u)) *
        Math.cos(2.0 * Math.PI * v);

    return mean + std * z;
}


function clamp(value, min, max) {

    return Math.min(
        Math.max(value, min),
        max
    );
}


function round2(value) {

    return Math.round(value * 100) / 100;

}


/* ============================================================
   AI EVALUATOR
   ============================================================ */

function evaluateAI(disclosure) {

    let historicalAdjustment = 0;

    /*
        STATIC AI

        The AI only looks at the current disclosure.
    */

    if (game.memoryMode === "static") {

        historicalAdjustment = 0;

    }


    /*
        NAIVE HISTORY

        The AI uses previous firm performance.

        IMPORTANT:

        It does NOT remove the effect of previous capital.

        This creates the feedback problem studied in the paper.
    */

    else if (
        game.memoryMode === "naive"
        &&
        game.history.length > 0
    ) {

        const recent =
            game.history[
                game.history.length - 1
            ];

        historicalAdjustment =
            0.35 *
            (
                recent.performance -
                recent.trueQuality
            );

    }


    /*
        CAPITAL-PURGED HISTORY

        The evaluator attempts to remove the part of
        performance explained by previous capital allocation.

        residual performance:

        performance
        - rho * capital
    */

    else if (
        game.memoryMode === "purged"
        &&
        game.history.length > 0
    ) {

        const recent =
            game.history[
                game.history.length - 1
            ];

        const capitalAdjustedPerformance =
            recent.performance -
            GAME_CONFIG.capitalProductivity *
            recent.capital;

        historicalAdjustment =
            0.35 *
            (
                capitalAdjustedPerformance -
                recent.trueQuality
            );

    }


    let score =
        disclosure +
        historicalAdjustment +
        randomNormal(
            0,
            GAME_CONFIG.valuationNoise
        );


    return clamp(
        score,
        0,
        GAME_CONFIG.maxQuality + 20
    );

}


/* ============================================================
   INTRO
   ============================================================ */

function startGame() {

    document
        .getElementById("intro")
        .classList.add("hidden");

    document
        .getElementById("setup")
        .classList.remove("hidden");

}


/* ============================================================
   ROLE SELECTION
   ============================================================ */

function chooseRole(role) {

    game.role = role;

    document
        .getElementById("setup")
        .classList.add("hidden");

    document
        .getElementById("memorySetup")
        .classList.remove("hidden");

}


/* ============================================================
   MEMORY MODE
   ============================================================ */

function setMemoryMode(mode) {

    game.memoryMode = mode;

    document
        .getElementById("memorySetup")
        .classList.add("hidden");

    game.round = 1;

    if (game.role === "investor") {

        document
            .getElementById("investorGame")
            .classList.remove("hidden");

        startInvestorRound();

    }

    else {

        document
            .getElementById("firmGame")
            .classList.remove("hidden");

        startFirmRound();

    }

}


/* ============================================================
   DISPLAY MEMORY MODE
   ============================================================ */

function memoryModeName() {

    if (game.memoryMode === "static") {

        return "No Memory";

    }

    if (game.memoryMode === "naive") {

        return "Naive History";

    }

    return "Capital-Purged History";

}


/* ============================================================
   INVESTOR GAME
   ============================================================ */

function startInvestorRound() {

    if (game.round > GAME_CONFIG.rounds) {

        finishGame();

        return;

    }


    const trueQuality =
        clamp(
            40 +
            randomNormal(0, 15),
            10,
            90
        );


    const manipulation =
        clamp(
            Math.abs(
                randomNormal(4, 4)
            ),
            0,
            15
        );


    const disclosure =
        trueQuality +
        manipulation;


    const aiValuation =
        evaluateAI(disclosure);


    const privateSignal =
        clamp(
            trueQuality +
            randomNormal(
                0,
                GAME_CONFIG.signalNoise
            ),
            0,
            100
        );


    const competitorBid =
        clamp(
            0.55 * trueQuality +
            0.25 * aiValuation +
            randomNormal(
                0,
                GAME_CONFIG.competitorNoise
            ),
            0,
            120
        );


    game.current = {

        trueQuality,

        manipulation,

        disclosure,

        aiValuation,

        privateSignal,

        competitorBid,

        capital: 0,

        performance: 0

    };


    document
        .getElementById("roundText")
        .textContent =
        `Round ${game.round} of ${GAME_CONFIG.rounds}`;


    document
        .getElementById("aiModeDisplay")
        .textContent =
        memoryModeName();


    document
        .getElementById("aiValuation")
        .textContent =
        round2(aiValuation);


    document
        .getElementById("privateSignal")
        .textContent =
        round2(privateSignal);


    document
        .getElementById("investorUtility")
        .textContent =
        round2(game.totalUtility);


    document
        .getElementById("bidInput")
        .value = "";


    document
        .getElementById("investorResult")
        .classList.add("hidden");


    document
        .getElementById("nextInvestorButton")
        .classList.add("hidden");

}


/* ============================================================
   INVESTOR BID
   ============================================================ */

function submitInvestorBid() {

    const bid =
        parseFloat(
            document
                .getElementById("bidInput")
                .value
        );


    if (
        Number.isNaN(bid) ||
        bid < 0
    ) {

        alert("Please enter a valid non-negative bid.");

        return;

    }


    const state =
        game.current;


    /*
        FIRST-PRICE ALLOCATION

        The investor wins if their bid exceeds
        the competing bid.

        Winner pays their own bid.
    */

    const won =
        bid >= state.competitorBid;


    let capital = 0;
    let payment = 0;
    let performance = state.trueQuality;


    if (won) {

        payment = bid;

        /*
            Capital received by the firm increases
            with the winning bid.

            This creates the feedback mechanism.
        */

        capital =
            clamp(
                GAME_CONFIG.baseCapital +
                0.5 * bid,
                0,
                GAME_CONFIG.maxCapital
            );


        performance =
            state.trueQuality +
            GAME_CONFIG.capitalProductivity *
            capital +
            randomNormal(0, 5);

    }


    const value =
        state.trueQuality;


    let utility;

    if (won) {

        utility =
            value -
            payment;

    }

    else {

        utility = 0;

    }


    const aiError =
        Math.abs(
            state.aiValuation -
            state.trueQuality
        );


    state.bid = bid;

    state.won = won;

    state.payment = payment;

    state.capital = capital;

    state.performance = performance;

    state.utility = utility;

    state.aiError = aiError;


    game.totalUtility += utility;

    game.totalAIError += aiError;

    game.totalAllocation +=
        capital;


    game.history.push({

        round: game.round,

        trueQuality:
            state.trueQuality,

        manipulation:
            state.manipulation,

        disclosure:
            state.disclosure,

        aiValuation:
            state.aiValuation,

        privateSignal:
            state.privateSignal,

        bid,

        competitorBid:
            state.competitorBid,

        allocation:
            won ? 1 : 0,

        payment,

        capital,

        performance,

        utility

    });


    showInvestorResult();

}


/* ============================================================
   INVESTOR RESULT
   ============================================================ */

function showInvestorResult() {

    const state =
        game.current;


    const result =
        document
            .getElementById("investorResult");


    result.classList.remove("hidden");


    let allocationText;


    if (state.won) {

        allocationText = `
            <strong>You won the share.</strong><br>
            Your payment: ${round2(state.payment)}<br>
            Capital allocated to the firm: ${round2(state.capital)}<br>
            Realized firm performance:
            ${round2(state.performance)}<br>
            Your utility:
            ${round2(state.utility)}
        `;

    }

    else {

        allocationText = `
            <strong>You did not win the share.</strong><br>
            Your bid: ${round2(state.bid)}<br>
            Competing bid:
            ${round2(state.competitorBid)}<br>
            Your utility: 0
        `;

    }


    result.innerHTML = `

        ${allocationText}

        <hr>

        <strong>Information revealed:</strong><br>

        True firm quality:
        ${round2(state.trueQuality)}<br>

        AI valuation:
        ${round2(state.aiValuation)}<br>

        Disclosure:
        ${round2(state.disclosure)}<br>

        Strategic manipulation:
        ${round2(state.manipulation)}<br>

        AI valuation error:
        ${round2(state.aiError)}

    `;


    document
        .getElementById("nextInvestorButton")
        .classList.remove("hidden");

}


/* ============================================================
   NEXT INVESTOR ROUND
   ============================================================ */

function nextInvestorRound() {

    game.round += 1;

    startInvestorRound();

}


/* ============================================================
   FIRM GAME
   ============================================================ */

function startFirmRound() {

    if (game.round > GAME_CONFIG.rounds) {

        finishGame();

        return;

    }


    const trueQuality =
        clamp(
            40 +
            randomNormal(0, 15),
            10,
            90
        );


    const aiValuation =
        evaluateAI(trueQuality);


    game.current = {

        trueQuality,

        aiValuation,

        manipulation: 0,

        disclosure: trueQuality,

        capital: 0,

        performance: trueQuality

    };


    document
        .getElementById("firmRoundText")
        .textContent =
        `Round ${game.round} of ${GAME_CONFIG.rounds}`;


    document
        .getElementById("trueQuality")
        .textContent =
        round2(trueQuality);


    document
        .getElementById("firmAiMode")
        .textContent =
        memoryModeName();


    updateManipulation();


    document
        .getElementById("firmProfit")
        .textContent =
        round2(game.totalProfit);


    document
        .getElementById("firmResult")
        .classList.add("hidden");


    document
        .getElementById("nextFirmButton")
        .classList.add("hidden");

}


/* ============================================================
   MANIPULATION SLIDER
   ============================================================ */

function updateManipulation() {

    const value =
        parseFloat(
            document
                .getElementById("manipulationInput")
                .value
        );


    document
        .getElementById("manipulationValue")
        .textContent =
        value.toFixed(1);


    const cost =
        GAME_CONFIG.manipulationCostCoefficient *
        value *
        value;


    document
        .getElementById("manipulationCost")
        .textContent =
        round2(cost);

}


/* ============================================================
   FIRM DECISION
   ============================================================ */

function submitFirmDecision() {

    const manipulation =
        parseFloat(
            document
                .getElementById("manipulationInput")
                .value
        );


    const state =
        game.current;


    const disclosure =
        state.trueQuality +
        manipulation;


    /*
        AI evaluates the manipulated disclosure.
    */

    const aiValuation =
        evaluateAI(disclosure);


    /*
        Competitor / investor bid

        This is intentionally simplified.

        Investors use both AI valuation and
        the underlying information structure.
    */

    const investorBid =
        clamp(
            0.65 * aiValuation +
            randomNormal(0, 8),
            0,
            120
        );


    /*
        Firm receives capital if the investor
        participates in the allocation.
    */

    const capital =
        clamp(
            GAME_CONFIG.baseCapital +
            0.5 * investorBid,
            0,
            GAME_CONFIG.maxCapital
        );


    /*
        Future performance depends on:

        true quality
        +
        capital productivity
        +
        random shock
    */

    const performance =
        state.trueQuality +
        GAME_CONFIG.capitalProductivity *
        capital +
        randomNormal(0, 5);


    const manipulationCost =
        GAME_CONFIG.manipulationCostCoefficient *
        manipulation *
        manipulation;


    /*
        Firm's simplified objective:

        capital received
        - manipulation cost
    */

    const profit =
        capital -
        manipulationCost;


    const aiError =
        Math.abs(
            aiValuation -
            state.trueQuality
        );


    state.manipulation =
        manipulation;

    state.disclosure =
        disclosure;

    state.aiValuation =
        aiValuation;

    state.investorBid =
        investorBid;

    state.capital =
        capital;

    state.performance =
        performance;

    state.manipulationCost =
        manipulationCost;

    state.profit =
        profit;

    state.aiError =
        aiError;


    game.totalProfit += profit;

    game.totalManipulation +=
        manipulation;

    game.totalAIError +=
        aiError;

    game.totalAllocation +=
        capital;


    game.history.push({

        round: game.round,

        trueQuality:
            state.trueQuality,

        manipulation,

        disclosure,

        aiValuation,

        investorBid,

        allocation: 1,

        capital,

        performance,

        manipulationCost,

        profit

    });


    showFirmResult();

}


/* ============================================================
   FIRM RESULT
   ============================================================ */

function showFirmResult() {

    const state =
        game.current;


    const result =
        document
            .getElementById("firmResult");


    result.classList.remove("hidden");


    result.innerHTML = `

        <strong>Round outcome</strong><br><br>

        True quality:
        ${round2(state.trueQuality)}<br>

        Strategic manipulation:
        ${round2(state.manipulation)}<br>

        Disclosure:
        ${round2(state.disclosure)}<br>

        AI valuation:
        ${round2(state.aiValuation)}<br>

        Investor bid:
        ${round2(state.investorBid)}<br>

        Capital received:
        ${round2(state.capital)}<br>

        Firm performance:
        ${round2(state.performance)}<br>

        Manipulation cost:
        ${round2(state.manipulationCost)}<br>

        Firm profit:
        ${round2(state.profit)}

    `;


    document
        .getElementById("nextFirmButton")
        .classList.remove("hidden");

}


/* ============================================================
   NEXT FIRM ROUND
   ============================================================ */

function nextFirmRound() {

    game.round += 1;

    startFirmRound();

}


/* ============================================================
   GAME FINISH
   ============================================================ */

function finishGame() {

    document
        .getElementById("investorGame")
        .classList.add("hidden");

    document
        .getElementById("firmGame")
        .classList.add("hidden");

    document
        .getElementById("summary")
        .classList.remove("hidden");


    const n =
        Math.max(
            game.history.length,
            1
        );


    const averageManipulation =
        game.totalManipulation / n;


    const averageAIError =
        game.totalAIError / n;


    const averageAllocation =
        game.totalAllocation / n;


    document
        .getElementById("summaryRounds")
        .textContent =
        game.history.length;


    document
        .getElementById("summaryManipulation")
        .textContent =
        round2(averageManipulation);


    document
        .getElementById("summaryAIError")
        .textContent =
        round2(averageAIError);


    document
        .getElementById("summaryAllocation")
        .textContent =
        round2(averageAllocation);


    if (game.role === "investor") {

        document
            .getElementById("summaryContent")
            .innerHTML = `

                <p>
                    You played as an investor.
                    Your total utility was
                    <strong>
                    ${round2(game.totalUtility)}
                    </strong>.
                </p>

                <p>
                    The experiment illustrates how investors
                    combine AI-generated public information
                    with private signals when allocating capital.
                </p>

            `;

    }

    else {

        document
            .getElementById("summaryContent")
            .innerHTML = `

                <p>
                    You played as a firm.
                    Your total simplified profit was
                    <strong>
                    ${round2(game.totalProfit)}
                    </strong>.
                </p>

                <p>
                    The experiment illustrates the trade-off
                    between strategic disclosure and the cost
                    of manipulating an AI evaluator.
                </p>

            `;

    }

}


/* ============================================================
   RESTART
   ============================================================ */

function restartGame() {

    game = {

        role: null,

        round: 1,

        memoryMode: "static",

        history: [],

        current: null,

        totalUtility: 0,

        totalProfit: 0,

        totalManipulation: 0,

        totalAIError: 0,

        totalAllocation: 0

    };


    document
        .getElementById("summary")
        .classList.add("hidden");

    document
        .getElementById("setup")
        .classList.remove("hidden");

}


/* ============================================================
   CSV EXPORT
   ============================================================ */

function exportCSV() {

    if (game.history.length === 0) {

        alert("No game data available.");

        return;

    }


    const headers = [

        "round",
        "trueQuality",
        "manipulation",
        "disclosure",
        "aiValuation",
        "privateSignal",
        "bid",
        "competitorBid",
        "allocation",
        "payment",
        "capital",
        "performance",
        "utility",
        "profit"

    ];


    const rows =
        game.history.map(
            row =>
                headers
                    .map(
                        h =>
                            row[h] !== undefined
                                ? row[h]
                                : ""
                    )
                    .join(",")
        );


    const csv =
        [
            headers.join(","),
            ...rows
        ].join("\n");


    const blob =
        new Blob(
            [csv],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(blob);


    const link =
        document.createElement("a");


    link.href = url;

    link.download =
        "strategic-disclosure-game-results.csv";


    link.click();


    URL.revokeObjectURL(url);

}


/* ============================================================
   OPTIONAL CONSOLE LOG
   ============================================================ */

console.log(
    "AI Valuation & Strategic Disclosure Game loaded."
);