/** @odoo-module **/
// Copyright 2026 DevsCodeSpace. License OPL-1.
import {
    clickOnSave,
    insertSnippet,
    registerWebsitePreviewTour,
} from "@website/js/tours/tour_utils";

registerWebsitePreviewTour("dcs_hero_block", {
    url: "/",
    edition: true,
}, () => [
    ...insertSnippet({
        id: "s_dcs_hero_shelf",
        name: "Shelf Hero",
        groupName: "DCS Commerce",
    }),
    {
        content: "The block is in the page",
        trigger: ":iframe #wrap .s_dcs_hero_shelf h1",
    },
    ...clickOnSave(),
    {
        content: "Saved and back in view mode",
        trigger: ":iframe body:not(.editor_enable) #wrap .s_dcs_hero_shelf .o_dcs_well img",
    },
]);
