from __future__ import annotations

import time
from html import escape

import matplotlib.pyplot as plt
import streamlit as st

from coin_abm import CoinModel


st.set_page_config(page_title="COIN ABM", page_icon="🧪", layout="wide")


def render_hover_label(label: str, description: str) -> None:
    st.markdown(
        f"<span title=\"{escape(description)}\" style=\"cursor: help;\">{escape(label)} <sup>ⓘ</sup></span>",
        unsafe_allow_html=True,
    )


def main() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
            color: #f8fafc;
        }
        .stButton > button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            border: 1px solid #2563eb;
            box-shadow: none;
            font-weight: 600;
            padding: 0.45rem 0.8rem;
        }
        .stButton > button:hover {
            background-color: #1d4ed8;
            border-color: #1d4ed8;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1.5rem;
        }
        div[data-testid="stForm"] {
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        .stSlider > div > div > div {
            color: #f8fafc;
        }
        .stMetric {
            background: #1f2937;
            border-radius: 10px;
            padding: 0.7rem 0.8rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("COIN Agent-Based Simulation Bennett(2008) Model Phase 1")
    st.caption("Configure the model in the form below and watch it evolve live in the UI.")

    with st.form("simulation_form"):
        st.subheader("Simulation parameters")

        col1, col2 = st.columns(2)

        with col1:
            render_hover_label(
                "Effectiveness",
                "Probability that a soldier successfully neutralizes an identified insurgent. Represents the operational capability of government forces. Higher values improve counterinsurgency success.",
            )
            effectiveness = st.slider("", 0.0, 1.0, 0.5, 0.01, key="effectiveness", label_visibility="collapsed")

            render_hover_label(
                "Accuracy",
                "Probability that intelligence correctly identifies the actual insurgent target. Determines intelligence quality. Low accuracy leads to collateral damage and increased insurgent recruitment.",
            )
            accuracy = st.slider("", 0.0, 1.0, 0.5, 0.01, key="accuracy", label_visibility="collapsed")

            render_hover_label(
                "P_GR",
                "Probability that insurgents successfully recruit a nearby civilian. Controls the growth rate of insurgency through recruitment.",
            )
            p_gr = st.slider("", 0.0, 1.0, 0.5, 0.01, key="p_gr", label_visibility="collapsed")

            render_hover_label(
                "P_IR",
                "Probability that a latent insurgent becomes an active insurgent. Determines how quickly passive support transforms into active violence.",
            )
            p_ir = st.slider("", 0.0, 1.0, 0.5, 0.01, key="p_ir", label_visibility="collapsed")

            render_hover_label(
                "P_IEWR",
                "Probability that an insurgent attack event succeeds. Represents insurgent operational effectiveness and ability to inflict damage.",
            )
            p_iewr = st.slider("", 0.0, 1.0, 0.5, 0.01, key="p_iewr", label_visibility="collapsed")

        with col2:
            render_hover_label("Soldier recruit count", "Number of nearby civilians a soldier can recruit in a single interaction.")
            soldier_recruit_n = st.slider("", 0, 9, 0, 1, key="soldier_recruit_n", label_visibility="collapsed")

            render_hover_label("Insurgent recruit count", "Number of nearby civilians an insurgent can recruit in a single interaction.")
            insurgent_recruit_n = st.slider("", 0, 9, 0, 1, key="insurgent_recruit_n", label_visibility="collapsed")

            render_hover_label("Soldier anger change", "How much a civilan's anger changes after an interaction with a soldier. Negative values indicate a decrease in anger, with positive values indicating an increase in anger.")
            soldier_anger_delta = st.slider("", -1.0, 1.0, -0.15, 0.01, key="soldier_anger_delta", label_visibility="collapsed")

            render_hover_label("Insurgent anger change", "How much an civilan's anger changes after an interaction with an insurgent. Negative values indicate a decrease in anger, with positive values indicating an increase in anger.")
            insurgent_anger_delta = st.slider("", -1.0, 1.0, 0.15, 0.01, key="insurgent_anger_delta", label_visibility="collapsed")

            render_hover_label("Random seed", "Random seed used for pseudo-random number generation. Ensures experimental reproducibility and consistent results.")
            seed = st.number_input("", min_value=1, value=1, step=1, key="seed", label_visibility="collapsed")

            render_hover_label("Maximum ticks", "Maximum number of simulation iterations. Prevents infinite simulations and defines the conflict duration limit.")
            max_ticks = st.number_input("", min_value=10, max_value=20000, value=5000, step=10, key="max_ticks", label_visibility="collapsed")

        show_live = st.checkbox("Show live simulation", value=True)
        interval_ms = st.slider("Animation interval (ms)", 0, 1000, 20, 10)
        render_every = st.slider("Refresh every N ticks", 1, 50, 5, 1)
        st.markdown(
            "<small style='color:#cbd5e1;'>Set a low interval and a higher refresh step to speed up live playback. "
            "Use `Refresh every N ticks` to render less often while the model still runs every tick.</small>",
            unsafe_allow_html=True,
        )
        submitted = st.form_submit_button("Run simulation")

        if submitted:
            model = CoinModel(
                effectiveness=effectiveness,
                accuracy=accuracy,
                p_gr=p_gr,
                p_ir=p_ir,
                p_iewr=p_iewr,
                soldier_recruit_n=soldier_recruit_n,
                soldier_anger_delta=soldier_anger_delta,
                insurgent_recruit_n=insurgent_recruit_n,
                insurgent_anger_delta=insurgent_anger_delta,
                seed=seed,
                max_ticks=max_ticks,
            )

            st.subheader("Live simulation")
            status = st.empty()
            progress_bar = st.progress(0.0)
            plot_placeholder = st.empty()

            if show_live:
                while model.termination_reason is None and model.tick_count < model.max_ticks:
                    model.step()
                    if model.tick_count % render_every == 0 or model.termination_reason is not None:
                        progress_value = min(model.tick_count / max_ticks, 1.0) if max_ticks > 0 else 1.0
                        progress_bar.progress(progress_value)
                        status.write(
                            f"Tick {model.tick_count}/{max_ticks} | "
                            f"Active={len(model._active_insurgents())} | "
                            f"Latent={len(model._latent_insurgents())}"
                        )
                        fig = model.summary_figure()
                        plot_placeholder.pyplot(fig)
                        plt.close(fig)
                    if interval_ms > 0:
                        time.sleep(interval_ms / 1000.0)
            else:
                model.run()
                progress_bar.progress(1.0)
                status.write("Simulation completed")

            st.success("Simulation completed")

            st.subheader("Results")
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric("Termination", model.termination_reason or "running")
            with col4:
                st.metric("Ticks", model.tick_count)
            with col5:
                st.metric("Insurgents killed", model.cumulative_insurgents_killed)

            final_fig = model.summary_figure()
            st.pyplot(final_fig)
            plt.close(final_fig)

            with st.expander("View history table"):
                st.dataframe(model.to_rows())


if __name__ == "__main__":
    main()
