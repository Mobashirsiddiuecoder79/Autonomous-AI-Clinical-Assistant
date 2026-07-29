import streamlit as st


# ==========================================================
# TIMELINE ITEM
# ==========================================================

def timeline_item(
    title: str,
    description: str = "",
    time: str = "",
    status: str = "completed"
):
    """
    Display a single timeline item.

    status:
        completed
        running
        pending
        error
    """

    icons = {
        "completed": "✅",
        "running": "🔄",
        "pending": "⏳",
        "error": "❌"
    }

    icon = icons.get(status, "•")

    with st.container(border=True):

        c1, c2 = st.columns([1, 12])

        with c1:
            st.markdown(f"## {icon}")

        with c2:

            st.markdown(f"**{title}**")

            if description:
                st.caption(description)

            if time:
                st.caption(f"🕒 {time}")


# ==========================================================
# TIMELINE
# ==========================================================

def timeline(
    items: list,
    title: str = "Activity Timeline"
):
    """
    Display a complete timeline.

    Example item:

    {
        "title": "...",
        "description": "...",
        "time": "...",
        "status": "completed"
    }
    """

    st.subheader(title)

    if not items:

        st.info("No activity available.")

        return

    for item in items:

        timeline_item(

            title=item.get(
                "title",
                "Unknown"
            ),

            description=item.get(
                "description",
                ""
            ),

            time=item.get(
                "time",
                ""
            ),

            status=item.get(
                "status",
                "completed"
            )

        )


# ==========================================================
# AGENT EXECUTION TIMELINE
# ==========================================================

def agent_timeline(
    plan: list,
    completed_tasks: list
):
    """
    Timeline for LangGraph execution.
    """

    st.subheader("🤖 Agent Execution")

    if not plan:

        st.info("No execution steps.")

        return

    for index, step in enumerate(plan, start=1):

        if step in completed_tasks:
            status = "completed"
        else:
            status = "pending"

        timeline_item(

            title=f"Step {index}",

            description=step,

            status=status

        )