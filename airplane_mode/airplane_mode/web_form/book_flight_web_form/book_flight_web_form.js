frappe.ready(function () {
    const params = new URLSearchParams(window.location.search);

    const flight = params.get("flight");
    const priceParam = params.get("flight_price");

    setTimeout(async function () {
        if (flight) {
            await frappe.web_form.set_value("flight", flight);
        }

        if (priceParam !== null && priceParam.trim() !== "") {
            const price = Number(priceParam);

            if (Number.isFinite(price)) {
                await frappe.web_form.set_value("flight_price", price);
            }
        }

        frappe.web_form.set_df_property(
            "flight_price",
            "read_only",
            1
        );
    }, 500);
});